import gh_types 
import attack_shapes as shapes

cards = [
    gh_types.ActionCard(
        attack_name="Fireball",
        actions=[gh_types.ElementAreaEffect(
            shape=shapes.circle(1),
            element="Fire",
            att_range=4
        )],
        movement=2,
        jump=False
    ),
    gh_types.ActionCard(
        attack_name="Cursed Frost Surge",
        actions=[
            gh_types.AreaAttack(
                shape=shapes.bar(1,2),
                strength=1
            ),
            gh_types.ElementAreaEffect(
                shape=shapes.bar(1,2),
                element="Ice",
                att_range=4
            )
        ],
        movement=2,
        jump=False
    ),
    gh_types.ActionCard(
        attack_name="Elementary Missile",
        actions=[gh_types.SingleTargetAttack(
            strength=5,
            att_range=4
        )],
        movement=0,
        jump=False
    ),
    gh_types.ActionCard(
        attack_name="Scholar's Escape",
        actions=[gh_types.SingleTargetAttack(
            strength=1,
            att_range=1
        )],
        movement=5,
        jump=False
    ),
    gh_types.ActionCard(
        attack_name="Masochistic Explosion",
        actions=[gh_types.ElementAreaEffect(
            att_range=1,
            element="Fire",
            shape=shapes.circle(2)
        )],
        movement=0,
        jump=False
    ),
    gh_types.ActionCard(
        attack_name="Lightning Bolt",
        actions=[gh_types.AreaAttack(
            shape=shapes.line((1,0), 3),
            strength=4
        )],
        movement=1,
        jump=False
    ),
    gh_types.ActionCard(
        attack_name="Random Teleport",
        actions=[
            gh_types.Teleport(
                att_range=1
            ),
            gh_types.SingleTargetAttack(
                strength=2,
                att_range=1
            )
        ],
        movement=1,
        jump=False
    ),
    gh_types.ActionCard(
        attack_name="B-Line",
        actions=[gh_types.AreaAttack(
            shape=shapes.line((0,1), 2),
            strength=2
        )],
        movement=2,
        jump=True
    ),
]

backstory = "wizards are cool"

health = 6
