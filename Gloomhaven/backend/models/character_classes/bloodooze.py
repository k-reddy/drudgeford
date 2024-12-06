from backend.models import action_model as actions
from backend.utils import attack_shapes as shapes
from backend.models import obstacle

cards = [
    actions.ActionCard(
        attack_name="Finishing Blow",
        actions=[
            actions.AreaAttackFromSelf(shape=shapes.arc(3), strength=1),
        ],
        movement=3,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Crimson Tendril",
        actions=[actions.Pull(3, 4), actions.SingleTargetAttack(3, 1)],
        movement=2,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Spliting Lash",
        actions=[
            actions.SingleTargetAttack(strength=3, att_range=3),
            actions.Teleport(3),
        ],
        movement=2,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Engulf",
        actions=[
            actions.Pull(2, 2),
            actions.AreaAttackFromSelf(shape=shapes.circle(1), strength=3),
        ],
        movement=2,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Necrotic Storm",
        actions=[
            actions.AreaAttackFromSelf(
                shape=shapes.ring(2), element_type=obstacle.RottingFlesh
            ),
            actions.WeakenAllEnemies(2, 2),
        ],
        movement=2,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Absorb Life",
        actions=[actions.SingleTargetAttack(3, 2), actions.ModifySelfHealth(2)],
        movement=2,
        jump=False,
    ),
]

health = 4
