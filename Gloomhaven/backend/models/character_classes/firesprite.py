from backend.models import action_model as actions
from backend.utils import attack_shapes as shapes
from backend.models import obstacle

cards = [
    actions.ActionCard(
        attack_name="Flame Darts",
        actions=[
            actions.SingleTargetAttack(2, 4),
            actions.SingleTargetAttack(1, 4),
        ],
        movement=3,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Fire Trail",
        actions=[
            actions.AreaAttackFromSelf(
                shape=shapes.line(4), element_type=obstacle.Fire, strength=1
            ),
            actions.WeakenAllEnemies(1, 2),
        ],
        movement=4,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Spark Storm",
        actions=[
            actions.AreaAttackFromSelf(shape=shapes.circle(1), strength=2),
        ],
        movement=3,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Burning Dash",
        actions=[
            actions.AreaAttackFromSelf(
                shape=shapes.cone(2), element_type=obstacle.Fire, strength=2
            ),
        ],
        movement=4,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Ember Shield",
        actions=[
            actions.ShieldAllAllies(1, 2, 2),
            actions.AreaAttackFromSelf(
                shape=shapes.ring(2), element_type=obstacle.Fire, strength=1
            ),
        ],
        movement=3,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Heat Wave",
        actions=[
            actions.WeakenAllEnemies(2, 2),
            actions.AreaAttackFromSelf(shapes.cone(2), 2),
        ],
        movement=3,
        jump=True,
    ),
]

health = 4
