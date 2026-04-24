from app.db.session import SessionLocal
from app.db.init_db import init
from app.db.models import KPIProfileModel

init()
db = SessionLocal()

CELL_ID = "cell_1"
TA = 10
WINDOW_SEC = 60

for bucket in range(60):
    existing = (
        db.query(KPIProfileModel)
        .filter(
            KPIProfileModel.cell_id == CELL_ID,
            KPIProfileModel.ta == TA,
            KPIProfileModel.time_bucket == bucket,
            KPIProfileModel.window_sec == WINDOW_SEC,
        )
        .first()
    )

    if existing:
        existing.mu = 2.0
        existing.sigma = 0.5
        existing.samples = 100
    else:
        db.add(
            KPIProfileModel(
                cell_id=CELL_ID,
                ta=TA,
                time_bucket=bucket,
                window_sec=WINDOW_SEC,
                mu=2.0,
                sigma=0.5,
                samples=100,
            )
        )

db.commit()
db.close()

print("Seeded KPI profiles for cell_1 / TA 10 across all 60-second buckets.")