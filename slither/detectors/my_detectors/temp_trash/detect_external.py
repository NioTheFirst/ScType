from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification


class detect_external(AbstractDetector):
    """
    Detects external functions
    """

    ARGUMENT = 'detect_external' # slither will launch the detector with slither.py --detect mydetector
    HELP = 'Help printed by slither'
    IMPACT = DetectorClassification.INFORMATIONAL
    CONFIDENCE = DetectorClassification.HIGH

    WIKI = 'Initialized i guess?'

    WIKI_TITLE = 'woops'
    WIKI_DESCRIPTION = 'i am initializing'
    WIKI_EXPLOIT_SCENARIO = 'finding external'
    WIKI_RECOMMENDATION = 'i will do something later'

    def _detect(self):
        results = []
        for contract in self.compilation_unit.contracts_derived:
            # Check if a function has 'backdoor' in its name
            for f in contract.functions:
                if(f.visibility == "external" or f.visibility == "public"):
                    info = ["External or Public function: ", f, "\n"]
                    res = self.generate_result(info)

                    results.append(res)
        return results
