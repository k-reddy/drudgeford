from backend.models import action_model as actions
from backend.utils import attack_shapes as shapes
from backend.models import obstacle

cards = [
    actions.ActionCard(
        attack_name="Dark Ritual",
        actions=[
            actions.CurseAllEnemies(2),
            actions.BlessAllAllies(2),
            actions.SingleTargetAttack(2, 2),
        ],
        movement=2,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Void Circle",
        actions=[
            actions.AreaAttackFromSelf(
                shape=shapes.circle(2), element_type=obstacle.Shadow, strength=1
            ),
            actions.WeakenAllEnemies(2, 2),
        ],
        movement=1,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Soul Link",
        actions=[actions.BlessAndFortifyAlly(2, 2), actions.HealAlly(2, 2)],
        movement=1,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Shadow Aegis",
        actions=[
            actions.ShieldAllAllies(3, 1, 3),
            actions.AreaAttackFromSelf(
                shape=shapes.ring(2), element_type=obstacle.Shadow, strength=1
            ),
        ],
        movement=1,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Curse of Weakness",
        actions=[actions.WeakenEnemy(3, 3), actions.CurseAllEnemies(2)],
        movement=2,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Dark Blessing",
        actions=[
            actions.Fortify(3),
            actions.AreaAttackFromSelf(
                shape=shapes.bar(1, 2), element_type=obstacle.Shadow, strength=1
            ),
        ],
        movement=1,
        jump=False,
    ),
]

health = 6
