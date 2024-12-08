import backend.models.action_model as actions
import backend.utils.attack_shapes as shapes

cards = [
    actions.ActionCard(
        attack_name="Forceful Strike",
        actions=[actions.SingleTargetAttack(4, 3), actions.Push(2, 3)],
        movement=4,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Sniper Shot",
        actions=[actions.SingleTargetAttack(5, 3)],
        movement=2,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Throwing Knives",
        actions=[
            actions.SingleTargetAttack(2, 2),
            actions.SingleTargetAttack(2, 2),
            actions.SingleTargetAttack(2, 2),
        ],
        movement=4,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Hook and Slice",
        actions=[actions.Pull(2, 3), actions.SingleTargetAttack(4, 1)],
        movement=3,
        jump=False,
    ),
    actions.ActionCard(
        attack_name="Whirlwind Assault",
        actions=[
            actions.AreaAttackFromSelf(shape=shapes.circle(1), strength=3),
            actions.Fortify(2),
        ],
        movement=3,
        jump=True,
    ),
    actions.ActionCard(
        attack_name="Vital Strike",
        actions=[actions.SingleTargetAttack(6, 1), actions.CurseSelf()],
        movement=2,
        jump=True,
    ),
]

health = 5
