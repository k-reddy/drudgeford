from backend.models import action_model as actions
from backend.utils import attack_shapes as shapes
from backend.models import obstacle

# Blue Dragon - Area control specialist
cards = [
    actions.ActionCard(
        attack_name="Piercing Stomp",
        actions=[
            actions.SingleTargetAttack(strength=5, att_range=1, knock_down=True),
        ],
        movement=2,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Biting Gale",
        actions=[
            actions.AreaAttackFromSelf(shape=shapes.circle(3), strength=3),
            actions.PushAllEnemies(2, 3),
        ],
        movement=3,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Ice Wall",
        actions=[
            actions.AreaAttackFromSelf(
                element_type=obstacle.Ice, shape=shapes.bar(1, 3)
            ),
            actions.ShieldSelf(2, 2),
        ],
        movement=2,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Wing Sweep",
        actions=[
            actions.AreaAttackFromSelf(shape=shapes.circle(1), strength=4),
            actions.PushAllEnemies(1, 1),
        ],
        movement=4,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Freezing Roar",
        actions=[
            actions.WeakenAllEnemies(2, 3),
            actions.AreaAttackFromSelf(
                shape=shapes.cone(3), element_type=obstacle.Ice, strength=3
            ),
            actions.SingleTargetAttack(1, 1, True),
        ],
        movement=2,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Territorial Strike",
        actions=[actions.SingleTargetAttack(4, 1, knock_down=True), actions.Push(2, 2)],
        movement=3,
        jump=True,
    ),
]

health = 10
