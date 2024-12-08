from backend.models import action_model as actions
from backend.utils import attack_shapes as shapes
from backend.models import obstacle

cards = [
    actions.ActionCard(
        attack_name="Shadow Veil",
        actions=[
            actions.AreaAttackFromSelf(
                shape=shapes.circle(2), element_type=obstacle.Shadow, strength=1
            ),
            actions.WeakenAllEnemies(2, 2),
        ],
        movement=3,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Nature's Blessing",
        actions=[actions.Fortify(2), actions.SingleTargetAttack(2, 3)],
        movement=3,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Fae Strike",
        actions=[actions.SingleTargetAttack(3, 2), actions.WeakenEnemy(2, 2)],
        movement=4,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Fairy Ring",
        actions=[
            actions.AreaAttackFromSelf(
                shape=shapes.ring(2), element_type=obstacle.Spores, strength=3
            )
        ],
        movement=3,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Shadow Dance",
        actions=[
            actions.Teleport(4),
            actions.AreaAttackFromSelf(
                shape=shapes.circle(1), element_type=obstacle.Shadow, strength=2
            ),
        ],
        movement=2,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Mystic Circle",
        actions=[actions.BlessAndFortifyAlly(2, 2), actions.HealAlly(3, 2)],
        movement=3,
        jump=True,
    ),
]

health = 3
