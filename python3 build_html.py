import os
import base64

# Output HTML file
output_file = "index.html"

# Folders to scan (update if your repo has different structure)
image_exts = ['.png', '.jpg', '.jpeg']
audio_exts = ['.mp3', '.wav', '.ogg']

image_assets = {}
audio_assets = {}

# Scan folders
for root, dirs, files in os.walk('.'):
    for file in files:
        name, ext = os.path.splitext(file)
        ext = ext.lower()
        path = os.path.join(root, file)
        if ext in image_exts:
            with open(path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode('utf-8')
                image_assets[name] = f"data:image/{ext[1:]};base64,{b64}"
        elif ext in audio_exts:
            with open(path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode('utf-8')
                audio_assets[name] = f"data:audio/{ext[1:]};base64,{b64}"

print(f"Found {len(image_assets)} images and {len(audio_assets)} audio files.")

# HTML template with embedded assets
html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Castle Crashers Demo</title>
<script src="https://cdn.jsdelivr.net/npm/phaser@3.60.0/dist/phaser.min.js"></script>
<style>
body {{ margin: 0; background: #000; }}
canvas {{ display: block; margin: 0 auto; }}
</style>
</head>
<body>
<script>
const imageAssets = {image_assets};
const audioAssets = {audio_assets};

const config = {{
    type: Phaser.AUTO,
    width: 800,
    height: 600,
    backgroundColor: '#87ceeb',
    physics: {{
        default: 'arcade',
        arcade: {{ gravity: {{ y: 500 }}, debug: false }}
    }},
    scene: {{
        preload: preload,
        create: create,
        update: update
    }}
}};

const game = new Phaser.Game(config);

let players = [], enemies = [], cursors, attackKey, magicKey;
let swordSound, hitSound, magicSound, bgm, magicGroup;
let attackCooldown = 0, magicCooldown = 0;

const knightMagicTypes = {{}};

function preload() {{
    for (const [key, data] of Object.entries(imageAssets)) {{
        this.load.image(key, data);
    }}
    for (const [key, data] of Object.entries(audioAssets)) {{
        this.load.audio(key, data);
    }}
    // Placeholder magic projectile if none exists
    if (!imageAssets['magicProjectile']) {{
        this.load.image('magicProjectile', 'https://i.ibb.co/6B9qzRn/magic.png');
    }}
}}

function create() {{
    const scene = this;

    // Background and ground
    const bgKey = Object.keys(imageAssets).find(k=>k.toLowerCase().includes('background'));
    if(bgKey) scene.add.image(400,300,bgKey).setScale(1);

    const groundKey = Object.keys(imageAssets).find(k=>k.toLowerCase().includes('ground'));
    const ground = scene.physics.add.staticGroup();
    if(groundKey) ground.create(400,580,groundKey).setScale(2).refreshBody();

    // Players
    const playerKeys = Object.keys(imageAssets).filter(k=>k.toLowerCase().startsWith('player'));
    playerKeys.forEach((key,i)=>{{
        const p = scene.physics.add.sprite(100+Math.random()*200,450,key);
        p.setBounce(0.2); p.setCollideWorldBounds(true); p.health=100; p.facing='right';
        scene.physics.add.collider(p,ground); players.push(p);
        // Assign knight-specific magic
        const types = ['fire','ice','lightning','poison'];
        const colors = [0xff0000,0x00ffff,0xffff00,0x00ff00];
        const speeds = [400,300,600,350];
        knightMagicTypes[key] = {{type:types[i%types.length],color:colors[i%types.length],speed:speeds[i%types.length]}};
    }});

    // Enemies
    const enemyKeys = Object.keys(imageAssets).filter(k=>!['background','ground'].some(n=>k.includes(n)) && !k.toLowerCase().startsWith('player'));
    enemyKeys.forEach(key=>{{
        const e = scene.physics.add.sprite(400+Math.random()*200,450,key);
        e.setBounce(0.2); e.setCollideWorldBounds(true); e.health=50;
        scene.physics.add.collider(e,ground); enemies.push(e);
    }});

    // Magic group
    magicGroup = scene.physics.add.group();
    scene.physics.add.collider(magicGroup,ground,proj=>proj.destroy());
    scene.physics.add.overlap(magicGroup,enemies,(proj,e)=>{{
        e.health-=25; hitSound.play(); proj.destroy();
        if(e.health<=0) e.destroy();
    }});

    // Input
    cursors = scene.input.keyboard.createCursorKeys();
    attackKey = scene.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.SPACE);
    magicKey = scene.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.M);

    // Sounds
    swordSound = scene.sound.add('sword',{volume:0.5});
    hitSound = scene.sound.add('hit',{volume:0.5});
    magicSound = scene.sound.add('magic',{volume:0.5});
    if(audioAssets['bgm']) bgm = scene.sound.add('bgm',{loop:true,volume:0.5}).play();
}}

function update(time, delta){{
    if(players.length===0) return;
    const speed = 200, jump=-400;
    attackCooldown-=delta; magicCooldown-=delta;
    const player = players[0];

    // Movement
    if(cursors.left.isDown){player.setVelocityX(-speed); player.facing='left';}
    else if(cursors.right.isDown){player.setVelocityX(speed); player.facing='right';}
    else player.setVelocityX(0);
    if(cursors.up.isDown && player.body.touching.down) player.setVelocityY(jump);

    // Sword attack
    if(attackKey.isDown && attackCooldown<=0){{
        swordSound.play(); attackCooldown=500;
        enemies.forEach(e=>{{if(Phaser.Math.Distance.Between(player.x,player.y,e.x,e.y)<50){{e.health-=20; hitSound.play();}}}});
        enemies = enemies.filter(e=>{{if(e.health<=0){{e.destroy(); return false;}} return true;}});
    }}

    // Magic attack
    if(magicKey.isDown && magicCooldown<=0){{
        magicCooldown=1000; magicSound.play();
        const projectile = magicGroup.create(player.x,player.y,'magicProjectile');
        const magicData = knightMagicTypes[Object.keys(knightMagicTypes)[0]];
        projectile.setVelocityX(player.facing==='right'?magicData.speed:-magicData.speed);
        projectile.setTint(magicData.color);
        projectile.setGravityY(-500);
    }}

    // Enemy AI
    enemies.forEach(e=>{{if(player.x<e.x) e.setVelocityX(-100); else e.setVelocityX(100);}});
}}
</script>
</body>
</html>
"""

# Write HTML file
with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_template)

print(f"✅ index.html generated! Double-click to play.")
