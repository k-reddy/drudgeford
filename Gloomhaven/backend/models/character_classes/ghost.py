from backend.models import action_model as actions
from backend.utils import attack_shapes as shapes
from backend.models import obstacle

cards = [
    actions.ActionCard(
        attack_name="Phase Strike",
        actions=[
            actions.SingleTargetAttack(3, 2),
            actions.Teleport(2),
        ],
        movement=3,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Spectral Chains",
        actions=[actions.Pull(3, 4), actions.CurseAllEnemies(2)],
        movement=2,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Haunting Mist",
        actions=[
            actions.AreaAttackFromSelf(
                shape=shapes.arc(4), element_type=obstacle.Shadow, strength=3
            ),
            actions.WeakenAllEnemies(1, 2),
        ],
        movement=3,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Possession",
        actions=[actions.Pull(2, 3), actions.BlessAllAllies(3)],
        movement=2,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Ethereal Dance",
        actions=[
            actions.Teleport(3),
            actions.AreaAttackFromSelf(
                shape=shapes.circle(2), element_type=obstacle.Shadow, strength=3
            ),
        ],
        movement=2,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Terror",
        actions=[
            actions.CurseAllEnemies(2),
            actions.AreaAttackFromSelf(shapes.circle(2), 1),
            actions.PushAllEnemies(2, 2),
        ],
        movement=2,
        jump=True,
    ),
]

health = 3
