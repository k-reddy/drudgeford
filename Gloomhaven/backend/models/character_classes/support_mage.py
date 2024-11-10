import backend.models.action_model as actions
import backend.utils.attack_shapes as shapes

magic_user_cards = [
    actions.ActionCard(
        attack_name="Cursed Bolt",
        actions=[
            actions.SingleTargetAttack(4, 3),
            actions.CurseAllEnemies(3)
        ],
        movement=1,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Blessing of Power",
        actions=[
            actions.BlessAndChargeAlly(3, 2),
            actions.HealAlly(3, 3)
        ],
        movement=1,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Weakening Ray",
        actions=[
            actions.SingleTargetAttack(2, 4),
            actions.WeakenEnemy(2,4)
        ],
        movement=1,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Protective Aura",
        actions=[
            actions.ShieldAllAllies(2, 2, 3),
            actions.BlessSelf()
        ],
        movement=1,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Banishing Ward",
        actions=[
            actions.ShieldSelf(2, 2),
            actions.BlessSelf(),
            actions.Teleport(3)
        ],
        movement=2,
        jump=True
    ),
    actions.ActionCard(
        attack_name="Chain Lightning",
        actions=[
            actions.SingleTargetAttack(3, 4),
            actions.AreaAttack(shape=shapes.line((0,1),3), strength=2)
        ],
        movement=1,
        jump=False
    ),

]

health = 3