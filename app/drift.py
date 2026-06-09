import logging
import numpy as np

try:
    from alibi_detect.cd import TabularDrift
    ALIBI_AVAILABLE = True
except Exception:
    TabularDrift = None
    ALIBI_AVAILABLE = False


REFERENCE_DATA = np.array([
    [5.1, 3.5, 1.4, 0.2],
    [4.9, 3.0, 1.4, 0.2],
    [6.2, 3.4, 5.4, 2.3],
    [5.9, 3.0, 5.1, 1.8],
    [6.7, 3.1, 4.7, 1.5],
    [5.6, 2.7, 4.2, 1.3]
])


class DriftDetector:
    def __init__(self):
        self.detector = None

        if ALIBI_AVAILABLE:
            try:
                self.detector = TabularDrift(
                    x_ref=REFERENCE_DATA,
                    p_val=0.05
                )
                logging.info("Alibi Detect drift detector initialized")
            except Exception as error:
                logging.warning(
                    f"Failed to initialize Alibi Detect: {error}"
                )

    def detect(self, features):

        data = np.array([features])

        if self.detector is not None:
            try:
                prediction = self.detector.predict(data)

                is_drift = (
                    prediction["data"]["is_drift"] == 1
                )

                if is_drift:
                    logging.warning(
                        "Drift detected by Alibi Detect"
                    )
                    return True

            except Exception as error:
                logging.warning(
                    f"Alibi Detect failed: {error}"
                )

        if np.mean(features) > 5:
            logging.warning(
                "Drift detected by fallback detector"
            )
            return True

        return False
