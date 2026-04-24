from collections import defaultdict
from datetime import datetime

def bucket_index(ts: datetime, window_sec: int) -> int:
    sec_of_hour = ts.minute * 60 + ts.second
    return sec_of_hour // window_sec

class SSDDetector:
    def __init__(self, threshold: float, sigma_floor: float, persistence_windows: int, block_duration_sec: int, neighbor_ta_span: int, action_ladder: list[float]):
        self.threshold = threshold
        self.sigma_floor = sigma_floor
        self.persistence_windows = persistence_windows
        self.block_duration_sec = block_duration_sec
        self.neighbor_ta_span = neighbor_ta_span
        self.action_ladder = sorted(action_ladder)
        self.persistence_state = defaultdict(int)

    def classify_action(self, score: float) -> str:
        if score > self.action_ladder[2]:
            return "reject"
        if score > self.action_ladder[1]:
            return "rate_limit"
        if score > self.action_ladder[0]:
            return "alert"
        return "none"

    def _neighbor_scores(self, ta: int, profiles_map: dict, counts_map: dict, bucket: int) -> tuple[float, float, float]:
        obs = 0.0
        mu = 0.0
        sigma_sq = 0.0
        found = False
        for n_ta in range(ta - self.neighbor_ta_span, ta + self.neighbor_ta_span + 1):
            if (n_ta, bucket) in profiles_map:
                p = profiles_map[(n_ta, bucket)]
                obs += counts_map.get(n_ta, 0)
                mu += p["mu"]
                sigma_sq += max(p["sigma"], self.sigma_floor) ** 2
                found = True
        if not found:
            return 0.0, 0.0, 0.0
        sigma = sigma_sq ** 0.5
        score = (obs - mu) / max(sigma, self.sigma_floor)
        return obs, mu, score

    def detect(self, cell_id: str, ts: datetime, counts_map: dict[int, int], profiles_map: dict[tuple[int, int], dict], window_sec: int) -> tuple[list[dict], list[dict]]:
        bucket = bucket_index(ts, window_sec)
        alarms = []
        policies = []

        for ta, observed_x in counts_map.items():
            prof = profiles_map.get((ta, bucket))
            if not prof:
                continue
            sigma = max(prof["sigma"], self.sigma_floor)
            score = (observed_x - prof["mu"]) / sigma

            _nobs, _nmu, nscore = self._neighbor_scores(ta, profiles_map, counts_map, bucket)
            final_score = max(score, nscore)
            action = self.classify_action(final_score)

            key = (cell_id, ta)
            if action != "none":
                self.persistence_state[key] += 1
            else:
                self.persistence_state[key] = 0

            if action != "none":
                alarms.append({
                    "ts": ts,
                    "cell_id": cell_id,
                    "ta": ta,
                    "observed_x": float(observed_x),
                    "mu": float(prof["mu"]),
                    "sigma": float(sigma),
                    "anomaly_score": float(final_score),
                    "threshold": float(self.threshold),
                    "action": action,
                })

                if action == "reject" and self.persistence_state[key] >= self.persistence_windows:
                    policies.append({
                        "created_at": ts,
                        "cell_id": cell_id,
                        "ta": ta,
                        "policy_type": "reject",
                        "duration_sec": self.block_duration_sec,
                        "status": "active",
                    })
                elif action == "rate_limit":
                    policies.append({
                        "created_at": ts,
                        "cell_id": cell_id,
                        "ta": ta,
                        "policy_type": "rate_limit",
                        "duration_sec": self.block_duration_sec,
                        "status": "active",
                    })

        return alarms, policies
