"""
Real-time Synthetic Transaction Simulator Service.
"""

import time
import random
import threading
import json
import numpy as np
from sqlalchemy.orm import Session

from backend.app.db.database import SessionLocal
from backend.app.db.models import Transaction, Prediction, FraudAlert
from backend.app.services.ml_service import ml_service


class TransactionSimulator:
    def __init__(self):
        self._is_running = False
        self._interval = 2.0
        self._thread = None
        self.total_simulated = 0
        self.alerts_generated = 0

    def start(self, interval_seconds: float = 2.0):
        if not self._is_running:
            self._is_running = True
            self._interval = max(0.5, interval_seconds)
            self._thread = threading.Thread(target=self._run_simulation_loop, daemon=True)
            self._thread.start()

    def stop(self):
        self._is_running = False

    def get_status(self):
        return {
            "is_running": self._is_running,
            "interval_seconds": self._interval,
            "total_simulated_transactions": self.total_simulated,
            "fraud_alerts_generated": self.alerts_generated
        }

    def _generate_synthetic_transaction(self) -> dict:
        """
        Generates realistic synthetic transaction feature dict with ~5% fraud probability.
        """
        is_fraud_sim = random.random() < 0.05
        tx_dict = {"time": round(time.time() % 172800, 2)}

        for i in range(1, 29):
            if is_fraud_sim and i in [14, 10, 4, 12]:
                # Inject anomalous distribution shift on key fraud features
                tx_dict[f"v{i}"] = round(random.gauss(-3.5, 1.2), 4)
            else:
                tx_dict[f"v{i}"] = round(random.gauss(0.0, 1.0), 4)

        tx_dict["amount"] = round(random.uniform(500.0, 3500.0) if is_fraud_sim else random.exponential(45.0), 2)
        return tx_dict

    def _run_simulation_loop(self):
        db: Session = SessionLocal()
        try:
            while self._is_running:
                tx_dict = self._generate_synthetic_transaction()

                db_tx = Transaction(
                    transaction_time=tx_dict["time"],
                    amount=tx_dict["amount"],
                    features_json=json.dumps(tx_dict)
                )
                db.add(db_tx)
                db.commit()
                db.refresh(db_tx)

                prob, is_fraud, risk_band, latency_ms = ml_service.predict(tx_dict)
                shap_contributions = ml_service.get_shap_contributions(tx_dict)

                db_pred = Prediction(
                    transaction_id=db_tx.id,
                    raw_probability=prob,
                    is_fraud_predicted=is_fraud,
                    risk_band=risk_band,
                    threshold_used=ml_service.threshold,
                    model_version=ml_service.model_version,
                    inference_time_ms=latency_ms,
                    shap_explanation_json=json.dumps(shap_contributions)
                )
                db.add(db_pred)
                db.commit()
                db.refresh(db_pred)

                self.total_simulated += 1

                if is_fraud or risk_band == "High":
                    db_alert = FraudAlert(
                        prediction_id=db_pred.id,
                        risk_score=prob,
                        status="New"
                    )
                    db.add(db_alert)
                    db.commit()
                    self.alerts_generated += 1

                time.sleep(self._interval)
        finally:
            db.close()


simulator_service = TransactionSimulator()
