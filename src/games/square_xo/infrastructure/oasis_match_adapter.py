"""Adapter from SquareXO result envelopes to platform blockchain ports."""


class OasisMatchAdapter:
    def __init__(self, result_service):
        self.result_service = result_service

    def submit_verified_result(self, envelope):
        return self.result_service.verify_and_submit(envelope)

