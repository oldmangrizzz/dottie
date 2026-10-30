"""Read-only inspection of the bounded, single-writer research event ledger."""
from pathlib import Path
from .ledger import EvidenceLedger


def audit_ledger(path):
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError('No ledger found. A missing log is not a clean run.')
    log = EvidenceLedger(path)
    count = log.verify()
    events = log._entries()
    requests = {}
    for event in events:
        payload = event.get('payload', {})
        if not isinstance(payload, dict):
            raise ValueError('Malformed receipt payload')
        kind = event.get('kind')
        request_id = payload.get('request_id')
        if not request_id:
            continue
        if kind == 'request_received':
            if request_id in requests:
                raise ValueError('Repeated request receipt despite idempotency rule')
            requests[request_id] = {'request_id': request_id,
                                    'event_types': [kind],
                                    'final_count': 0,
                                    'status': 'NOT_FINISHED'}
        else:
            if request_id not in requests:
                raise ValueError('Orphan event with no request_received: ' + str(request_id))
            current = requests[request_id]
            current['event_types'].append(kind)
            if kind in ('cognition.report_recorded', 'finding_recorded'):
                current['final_count'] += 1
                current['status'] = payload.get('status') or payload.get('claim_status') or 'RECORDED'
    result = []
    for req in requests.values():
        if req['final_count'] > 1:
            raise ValueError('Multiple final records for one request: ' + req['request_id'])
        finished = req.pop('final_count') == 1
        req['recovery_state'] = 'FINISHED_WITH_RECORDED_STATUS' if finished else 'PENDING_OPERATOR_RECONCILIATION'
        req['safe_to_auto_retry'] = False
        result.append(req)
    return {
        'ledger_state': 'HASH_CHAIN_VERIFIED_NOT_INDEPENDENTLY_ANCHORED',
        'total_events': count,
        'requests': result,
        'live_system_examined': False,
        'safe_to_auto_retry_any': False,
    }
