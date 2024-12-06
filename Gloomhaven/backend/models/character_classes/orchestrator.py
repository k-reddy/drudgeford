from backend.models import action_model as actions
from backend.utils import attack_shapes as shapes
from backend.models import obstacle

# The Orchestrator - Reality-bending puppet master boss
cards = [
    actions.ActionCard(
        attack_name="Pull Strings",
        actions=[actions.SummonPuppet(), actions.WeakenAllEnemies(1, 2)],
        movement=0,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Reality Warp",
        actions=[
            actions.AreaAttackFromSelf(
                shape=shapes.cone(3), element_type=obstacle.Shadow, strength=3
            ),
            actions.Teleport(3),
            actions.Teleport(4),
            actions.Teleport(5),
            actions.SingleTargetAttack(4, 6, True),
        ],
        movement=3,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Nightmare Web",
        actions=[
            actions.AreaAttackFromSelf(
                element_type=obstacle.Trap, shape=shapes.ring(2)
            ),
            actions.Pull(2, 3),
            actions.PushAllEnemies(2, 3),
            actions.CurseAllEnemies(3),
        ],
        movement=2,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Dance of Darkness",
        actions=[
            actions.AreaAttackFromSelf(
                shape=shapes.circle(2), element_type=obstacle.Shadow
            ),
            actions.SingleTargetAttack(strength=4, att_range=2, knock_down=True),
            actions.WeakenAllEnemies(2, 2),
            actions.HealAllAllies(3, 3),
        ],
        movement=3,
        jump=True,
    ),
]

health = 15
