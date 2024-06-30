def serialize_report(report):
    """Helper function to serialize MongoDB reports"""
    report['_id'] = str(report['_id'])
    return report