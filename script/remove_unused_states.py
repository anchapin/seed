from seed.models import Property
from seed.models import PropertyView
from seed.models import PropertyState
from seed.models import PropertyAuditLog


def get_all_auditlogs_to_depth(head, depth):
    """get all auditlogs in a tree up to depth
    """
    if depth < 1:
            return []
    elif depth == 1:
        return [head]
    else:
        r = [head]
        if head.parent1:
            r += get_all_auditlogs_to_depth(head.parent1, depth-1)
        if head.parent2:
            r += get_all_auditlogs_to_depth(head.parent2, depth-1)
        return r 


def state_ids_in_memorable_history(property, depth):
    """get states = or < than five states deep from the auditlog of
       state of the view of the newest cycle for the property.
    """
    newest_view = PropertyView.objects.filter(property=property).order_by("-cycle__start").first()
    auditlog_head = PropertyAuditLog.objects.get(state=newest_view.state)
    memorable_auditlogs = get_all_auditlogs_to_depth(auditlog_head, depth)

    return [al.state for al in memorable_auditlogs]


def get_keeper_state_ids(depth=5):
    """get states ids that are either

        1. attatched to views
        2. = or < than five states deep from the auditlog of
        state of the view of the newest cycle for each property.
    """
    keeper_state_ids = set()

    # keep states attatched to views
    viewed_states = PropertyState.objects.filter(propertyview__isnull=False).values_list("id", flat=True)
    keeper_state_ids.update(viewed_states)

    # for the newest view of each property, keep the states
    # connected to aduitlog = or < than five states deep
    for property in Property.objects.all():
        memorable_state = state_ids_in_memorable_history(property, depth)
        memorable_state_ids = [s.id for s in memorable_state]
        keeper_state_ids.update(memorable_state_ids)

    return keeper_state_ids


def delete_unneed_states():
    """delete all but memorable states
    """
    keeper_state_ids = get_keeper_state_ids()
    PropertyState.objects.exclude(id__in=keeper_state_ids).delete()
