from backend.models import action_model as actions
from backend.utils import attack_shapes as shapes
from backend.models import obstacle

cards = [
    actions.ActionCard(
        attack_name="Putrid Burst",
        actions=[
            actions.AreaAttackFromSelf(
                shape=shapes.cone(2), strength=1, element_type=obstacle.InfectedOoze
            ),
            actions.WeakenAllEnemies(1, 2),
        ],
        movement=2,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Infectious Trail",
        actions=[
            actions.AreaAttackFromSelf(
                shape=shapes.line(3), element_type=obstacle.InfectedOoze, strength=1
            ),
            actions.WeakenAllEnemies(1, 2),
        ],
        movement=3,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Festering Touch",
        actions=[actions.SingleTargetAttack(2, 1), actions.Curse(1)],
        movement=2,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Flesh Purge",
        actions=[
            actions.AreaAttackFromSelf(shape=shapes.cone(2), strength=1),
            actions.CurseAllEnemies(2),
        ],
        movement=2,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Corpse Explosion",
        actions=[
            actions.ModifySelfHealth(-2),
            actions.AreaAttackFromSelf(shape=shapes.circle(2), strength=2),
        ],
        movement=1,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Sickening Aura",
        actions=[actions.WeakenAllEnemies(2, 2), actions.CurseAllEnemies(2)],
        movement=2,
        jump=False,
    ),
]

health = 7
