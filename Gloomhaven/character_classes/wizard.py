import actions 
import attack_shapes as shapes
import obstacle 

cards = [
    actions.ActionCard(
        attack_name="Fireball",
        actions=[actions.ElementAreaEffectWithTarget(
            shape=shapes.circle(1),
            element_type=obstacle.Fire,
            att_range=4
        )],
        movement=2,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Cursed Frost Surge",
        actions=[
            actions.AreaAttack(
                shape=shapes.bar(1,2),
                strength=1
            ),
            actions.ElementAreaEffectFromSelf(
                shape=shapes.bar(1,2),
                element_type=obstacle.Ice,
            )
        ],
        movement=2,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Elementary Missile",
        actions=[actions.SingleTargetAttack(
            strength=5,
            att_range=4
        )],
        movement=0,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Scholar's Escape",
        actions=[actions.SingleTargetAttack(
            strength=1,
            att_range=1
        )],
        movement=5,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Masochistic Explosion",
        actions=[actions.ElementAreaEffectFromSelf(
            element_type=obstacle.Fire,
            shape=shapes.circle(2)
        )],
        movement=0,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Lightning Bolt",
        actions=[actions.AreaAttack(
            shape=shapes.line((1,0), 3),
            strength=4
        )],
        movement=1,
        jump=False
    ),
    actions.ActionCard(
        attack_name="Random Teleport",
        actions=[
            actions.Teleport(
                att_range=1
            ),
            actions.SingleTargetAttack(
                strength=2,
                att_range=1
            )
        ],
        movement=1,
        jump=False
    ),
    actions.ActionCard(
        attack_name="B-Line",
        actions=[actions.AreaAttack(
            shape=shapes.line((0,1), 2),
            strength=2
        )],
        movement=2,
        jump=True
    ),
]

backstory = "wizards are cool"

health = 6
