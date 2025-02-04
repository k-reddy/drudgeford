from backend.models import action_model as actions
from backend.utils import attack_shapes as shapes
from backend.models import obstacle

cards = [
    actions.ActionCard(
        attack_name="Piercing Claws",
        actions=[actions.SingleTargetAttack(4, 1, pierce=True)],
        movement=2,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Brutal Slam",
        actions=[actions.SingleTargetAttack(2, 1, knock_down=True), actions.Push(3, 1)],
        movement=1,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Chain Pull",
        actions=[
            actions.Pull(4, 4),
            actions.SingleTargetAttack(3, 1, knock_down=True),
            actions.Push(2, 1),
        ],
        movement=1,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Defensive Wings",
        actions=[actions.ShieldSelf(3, 1), actions.Push(2, 2)],
        movement=2,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Blood Frenzy",
        actions=[actions.SingleTargetAttack(2, 1), actions.ModifySelfHealth(3)],
        movement=1,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Intimidating Presence",
        actions=[actions.WeakenAllEnemies(2, 2), actions.PushAllEnemies(2, 2)],
        movement=1,
        jump=True,
    ),
]

health = 5
