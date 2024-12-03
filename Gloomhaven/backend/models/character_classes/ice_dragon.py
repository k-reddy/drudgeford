from backend.models import action_model as actions
from backend.utils import attack_shapes as shapes
from backend.models import obstacle

# Blue Dragon - Area control specialist
cards = [
    actions.ActionCard(
        attack_name="Frost Breath",
        actions=[
            actions.AreaAttack(shape=shapes.cone(3), strength=2),
            actions.ElementAreaEffectFromSelf(
                shape=shapes.cone(3), element_type=obstacle.Ice
            ),
        ],
        movement=2,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Biting Gale",
        actions=[
            actions.SingleTargetAttack(4, 1),
            actions.PushAllEnemies(2, 3),
        ],
        movement=3,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Ice Wall",
        actions=[
            actions.ElementAreaEffectFromSelf(
                element_type=obstacle.Ice, shape=shapes.bar(1, 3)
            ),
            actions.ShieldSelf(2, 2),
        ],
        movement=2,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Wing Buffet",
        actions=[
            actions.AreaAttack(shape=shapes.circle(1), strength=2),
            actions.PushAllEnemies(1, 1),
        ],
        movement=4,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Freezing Roar",
        actions=[
            actions.WeakenAllEnemies(2, 3),
            actions.ElementAreaEffectFromSelf(
                shape=shapes.ring(2), element_type=obstacle.Ice
            ),
        ],
        movement=2,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Territorial Strike",
        actions=[actions.SingleTargetAttack(4, 2), actions.Push(2, 2)],
        movement=3,
        jump=True,
    ),
]

health = 10
