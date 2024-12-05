from backend.models import action_model as actions
from backend.utils import attack_shapes as shapes
from backend.models import obstacle

cards = [
    actions.ActionCard(
        attack_name="Putrid Burst",
        actions=[
            actions.AreaAttack(shape=shapes.cone(2), strength=1),
            actions.WeakenAllEnemies(2, 2),
        ],
        movement=2,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Infectious Trail",
        actions=[
            actions.ElementAreaEffectFromSelf(
                shape=shapes.line(3), element_type=obstacle.Spores
            ),
            actions.WeakenAllEnemies(1, 2),
        ],
        movement=3,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Festering Touch",
        actions=[actions.SingleTargetAttack(3, 1), actions.Curse(1)],
        movement=2,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Flesh Purge",
        actions=[
            actions.AreaAttack(shape=shapes.cone(2), strength=2),
            actions.CurseAllEnemies(2),
        ],
        movement=2,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Corpse Explosion",
        actions=[
            actions.ModifySelfHealth(-2),
            actions.AreaAttack(shape=shapes.circle(2), strength=3),
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

health = 4
