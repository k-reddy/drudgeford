from backend.models import action_model as actions
from backend.utils import attack_shapes as shapes

cards = [
    actions.ActionCard(
        attack_name="Crushing Advance",
        actions=[actions.SingleTargetAttack(3, 1)],
        movement=2,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Defensive Stance",
        actions=[actions.ShieldSelf(3, 1), actions.SingleTargetAttack(4, 1)],
        movement=2,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Sweeping Blow",
        actions=[actions.AreaAttackFromSelf(shape=shapes.cone(2), strength=2)],
        movement=3,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Shield Wall",
        actions=[
            actions.ShieldAllAllies(2, 1, 3),
            actions.ModifySelfHealth(2),
            actions.ChargeNextAttack(2),
        ],
        movement=0,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Grappling Strike",
        actions=[
            actions.Pull(2, 3),
            actions.SingleTargetAttack(3, 1),
        ],
        movement=1,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Shield Bash",
        actions=[actions.SingleTargetAttack(4, 1), actions.Push(2, 1)],
        movement=2,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Recuperating Blow",
        actions=[actions.SingleTargetAttack(4, 1), actions.ModifySelfHealth(2)],
        movement=2,
        jump=False,
    ),
]

health = 7
