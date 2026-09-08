#!/usr/bin/env python3
"""Convierte la lista de objetos de Pokemon 5E en el catalogo JS del tablero."""
import re, io, sys

LISTA = io.open('objetos.txt', encoding='utf-8').read()

CAT = {
    'pokeball':     'Poké Balls',
    'medicine':     'Medicinas',
    'berry':        'Bayas',
    'evolution':    'Evolución',
    'held item':    'Objetos equipados',
    'trainer gear': 'Equipo de entrenador',
}
ORDEN = ['Poké Balls', 'Medicinas', 'Bayas', 'Evolución',
         'Objetos equipados', 'Equipo de entrenador', 'Llaves de Nubia']

# ---------------------------------------------------------------- descripciones
D = {
 'Poké Ball':'La ball básica. Sirve para casi cualquier captura de rutina.',
 'Great Ball':'Captura con más facilidad que la Poké Ball.',
 'Ultra Ball':'La mejor ball de venta libre.',
 'Master Ball':'Captura sin fallar. No se vende: se gana.',
 'Safari Ball':'Ball de caña reservada a las zonas safari.',
 'Fast Ball':'Muy eficaz contra Pokémon que huyen.',
 'Level Ball':'Mejor cuanto más alto sea el nivel de tu Pokémon.',
 'Lure Ball':'Pensada para Pokémon pescados.',
 'Heavy Ball':'Mejor contra Pokémon muy pesados.',
 'Love Ball':'Eficaz si comparten especie y son de sexo opuesto.',
 'Friend Ball':'El Pokémon capturado empieza más encariñado.',
 'Moon Ball':'Eficaz contra los que evolucionan con Piedra Lunar.',
 'Sport Ball':'Ball del concurso de captura de bichos.',
 'Net Ball':'Pensada para Pokémon de agua y bicho.',
 'Dive Ball':'Funciona mejor bajo el agua.',
 'Nest Ball':'Más eficaz contra Pokémon de nivel bajo.',
 'Repeat Ball':'Eficaz contra especies que ya registraste.',
 'Timer Ball':'Mejora con cada turno que dura el combate.',
 'Luxury Ball':'Cómoda y acogedora: el Pokémon se encariña antes.',
 'Premier Ball':'Ball conmemorativa. Funciona como una Poké Ball.',
 'Dusk Ball':'Mejor de noche o dentro de cuevas.',
 'Heal Ball':'Cura por completo al Pokémon capturado.',
 'Quick Ball':'Muy eficaz en el primer turno del encuentro.',
 'Dream Ball':'Solo funciona con Pokémon dormidos.',
 'Potion':'Restaura unos pocos puntos de salud.',
 'Super Potion':'Restaura una cantidad media de salud.',
 'Hyper Potion':'Restaura una gran cantidad de salud.',
 'Max Potion':'Devuelve toda la salud a un Pokémon.',
 'Full Restore':'Cura del todo y quita los estados alterados.',
 'Full Heal':'Quita cualquier estado alterado.',
 'Antidote':'Cura el envenenamiento.',
 'Burn Heal':'Cura las quemaduras.',
 'Ice Heal':'Descongela a un Pokémon.',
 'Awakening':'Despierta a un Pokémon dormido.',
 'Paralyze Heal':'Cura la parálisis.',
 'Revive':'Reanima a un debilitado con la mitad de su salud.',
 'Max Revive':'Reanima a un debilitado con toda su salud.',
 'Sacred Ash':'Revive y cura por completo a todo el equipo.',
 'Fresh Water':'Agua de manantial. Restaura poca salud.',
 'Soda Pop':'Bebida con gas. Restaura algo más que el agua.',
 'Berry Juice':'Zumo de bayas. Restaura salud modestamente.',
 'Lemonade':'Bebida ácida. Buena recuperación por su precio.',
 'Moomoo Milk':'Leche espesa que restaura bastante salud.',
 'Energy Powder':'Polvo amargo que restaura salud. A los Pokémon no les gusta.',
 'Energy Root':'Raíz amarga muy eficaz, pero baja el ánimo.',
 'Heal Powder':'Polvo amargo que quita estados alterados.',
 'Revival Herb':'Hierba amarguísima que revive por completo.',
 'Ether':'Recupera los usos de un movimiento.',
 'Max Ether':'Recupera todos los usos de un movimiento.',
 'Elixir':'Recupera usos de todos los movimientos.',
 'Max Elixir':'Recupera del todo los usos de todos los movimientos.',
 'HP Up':'Sube permanentemente los puntos de salud.',
 'Protein':'Sube permanentemente el ataque.',
 'Iron':'Sube permanentemente la defensa.',
 'Carbos':'Sube permanentemente la velocidad.',
 'Calcium':'Sube permanentemente el ataque especial.',
 'Zinc':'Sube permanentemente la defensa especial.',
 'PP Up':'Amplía los usos máximos de un movimiento.',
 'Ability Capsule':'Cambia la habilidad del Pokémon por su alternativa.',
 'Guard Spec':'Impide que bajen las características este combate.',
 'Dire Hit':'Aumenta mucho la probabilidad de golpe crítico.',
 'Sun Stone':'Hace evolucionar a ciertos Pokémon de planta y fuego.',
 'Moon Stone':'Hace evolucionar a ciertos Pokémon de hada.',
 'Fire Stone':'Hace evolucionar a ciertos Pokémon de fuego.',
 'Thunder Stone':'Hace evolucionar a ciertos Pokémon eléctricos.',
 'Water Stone':'Hace evolucionar a ciertos Pokémon de agua.',
 'Leaf Stone':'Hace evolucionar a ciertos Pokémon de planta.',
 'Shiny Stone':'Provoca evoluciones ligadas a la luz.',
 'Dusk Stone':'Provoca evoluciones ligadas a la oscuridad.',
 'Dawn Stone':'Provoca evoluciones ligadas al amanecer.',
 'Ice Stone':'Hace evolucionar a ciertos Pokémon de hielo.',
 'Oval Stone':'Piedra con forma de huevo. Provoca una evolución.',
 'Alola Stone':'Piedra regional que despierta formas de Alola.',
 'Air Balloon':'Deja al portador flotando hasta que lo golpean.',
 'Assault Vest':'Sube la defensa especial pero prohíbe movimientos de apoyo.',
 'Big Root':'Aumenta la salud robada por drenaje.',
 'Black Sludge':'Cura a los de veneno y daña a los demás.',
 'Eject Button':'Saca al portador del combate al recibir un golpe.',
 'Eviolite':'Sube las defensas de los que aún pueden evolucionar.',
 'Exp Share':'Reparte la experiencia con el resto del equipo.',
 'Focus Band':'Puede resistir con un punto de salud un golpe letal.',
 'Focus Sash':'Resiste con un punto de salud si estaba al máximo.',
 'Leftovers':'Recupera un poco de salud cada turno.',
 "King's Rock":'Puede hacer retroceder al rival. También provoca evoluciones.',
 'Muscle Band':'Refuerza los movimientos físicos.',
 'Quick Claw':'A veces permite atacar primero.',
 'Razor Claw':'Aumenta los críticos. También provoca evoluciones.',
 'Razor Fang':'Puede hacer retroceder. También provoca evoluciones.',
 'Scope Lens':'Aumenta la probabilidad de golpe crítico.',
 'Shell Bell':'Recupera salud proporcional al daño causado.',
 'Smoke Ball':'Permite huir siempre de los Pokémon salvajes.',
 'Wide Lens':'Mejora un poco la precisión.',
 'Wise Glasses':'Refuerza los movimientos especiales.',
 'Megalite Stone':'Piedra que permite la megaevolución.',
 'Mirror Herb':'Copia las subidas de característica del rival.',
 'Choice Band':'Sube el ataque pero encierra en un solo movimiento.',
 'Choice Scarf':'Sube la velocidad con la misma limitación.',
 'Choice Specs':'Sube el ataque especial con la misma limitación.',
 'Flame Orb':'Quema al portador al final del turno.',
 'Life Orb':'Aumenta el daño a costa de salud propia.',
 'Toxic Orb':'Envenena gravemente al portador.',
 'Damp Rock':'Alarga la lluvia.',
 'Heat Rock':'Alarga el sol abrasador.',
 'Icy Rock':'Alarga el granizo.',
 'Smooth Rock':'Alarga la tormenta de arena.',
 'DNA Splicer':'Fusiona y separa a Kyurem con sus compañeros.',
 'Deep Sea Scale':'Escama del fondo marino. Provoca una evolución.',
 'Deep Sea Tooth':'Colmillo del fondo marino. Provoca una evolución.',
 'Gracidea Flower':'Flor que cambia la forma de Shaymin.',
 'Griseous Orb':'Orbe que mantiene la forma origen de Giratina.',
 'Leek':'Puerro largo. Sube mucho los críticos de Farfetch\u2019d.',
 'Light Ball':'Duplica el ataque de Pikachu.',
 'Lucky Punch':'Sube mucho los críticos de Chansey.',
 'Metal Powder':'Sube la defensa de Ditto sin transformar.',
 'N-Solarizer':'Fusiona a Necrozma con Solgaleo.',
 'N-Lunarizer':'Fusiona a Necrozma con Lunala.',
 'Prison Bottle':'Botella que despierta la forma cautiva de Hoopa.',
 'Reveal Glass':'Espejo que cambia la forma de los genios.',
 'Thick Club':'Duplica el ataque de Cubone y Marowak.',
 'Blue Orb':'Orbe que despierta a Kyogre.',
 'Red Orb':'Orbe que despierta a Groudon.',
 'Dragon Scale':'Escama dura. Provoca una evolución.',
 'Upgrade':'Dispositivo de Silph. Provoca una evolución.',
 'Protector':'Armadura pesada. Provoca una evolución.',
 'Electirizer':'Caja con carga eléctrica. Provoca una evolución.',
 'Magmarizer':'Caja llena de magma. Provoca una evolución.',
 'Dubious Disc':'Disco con datos sospechosos. Provoca una evolución.',
 'Reaper Cloth':'Tela impregnada de energía. Provoca una evolución.',
 'Prism Scale':'Escama irisada. Provoca una evolución.',
 'Whipped Dream':'Nata dulce. Provoca una evolución.',
 'Sachet':'Bolsita perfumada. Provoca una evolución.',
 'Sweet':'Dulce decorativo que da forma a Alcremie.',
 "Trainer's License":'Acredita tu registro oficial como entrenador.',
 'Pokédex':'Registra las especies que veas y te da su ficha.',
 'Old Rod':'Caña sencilla. Pesca en aguas someras.',
 'Good Rod':'Caña decente. Alcanza a más especies.',
 'Super Rod':'Caña profesional. Llega a las aguas profundas.',
 'Escape Rope':'Devuelve al grupo a la entrada de una cueva o edificio.',
 'Honey':'Untada en un árbol, atrae Pokémon salvajes.',
 'Key Stone':'Piedra que activa la megaevolución.',
 'Z-Ring':'Anillo que canaliza el poder de los cristales Z.',
 'Dynamax Band':'Brazalete que permite el fenómeno Dinamax.',
 'Tera Orb':'Orbe que activa la teracristalización.',
 'Capture Styler':'Aparato que somete Pokémon sin combatir.',
 'Backpack':'Mochila de viaje. Aumenta lo que puedes cargar.',
 'Binoculars':'Duplica el alcance de la percepción a distancia.',
 'Camping Kettle':'Hervidor de campamento.',
 'Camping Stove':'Hornillo portátil para cocinar en ruta.',
 'Canteen':'Cantimplora. Un día de agua.',
 'Energy Cell':'Pila recargable para aparatos pequeños.',
 'Flashlight':'Linterna de mano. Ilumina veinte metros.',
 'Solar Flashlight':'Linterna solar. No necesita pilas.',
 'Flint and Steel':'Pedernal y eslabón para encender fuego.',
 "Climber's Kit":'Cuerdas y clavos para escalar sin tirada.',
 'Cooking Kit':'Utensilios completos de cocina de campaña.',
 "Diver's Kit":'Equipo de buceo ligero.',
 "Gardener's Kit":'Herramientas para cultivar y recolectar bayas.',
 'Lantern':'Farol de aceite. Ilumina un campamento entero.',
 'Solar Lantern':'Farol solar. Se carga de día.',
 'Mess Kit':'Plato, cubiertos y taza de campaña.',
 'Multi-tool':'Herramienta plegable con doce funciones.',
 'Pocket Knife':'Navaja pequeña pero útil.',
 'Camping Ration':'Comida seca para un día de viaje.',
 'Rebreather':'Respirador que da una hora bajo el agua.',
 'Rebreather Filter':'Filtro de repuesto para el respirador.',
 'Sleeping Bag':'Saco de dormir. Permite descanso largo a la intemperie.',
 'Solar Charger':'Cargador solar para todo el equipo del grupo.',
 'Small Tent':'Tienda para dos personas.',
 'Large Tent':'Tienda para cuatro personas.',
 'Artisan Tools':'Herramientas de oficio para reparar y fabricar.',
 "Thieves' Tools":'Ganzúas y alambres. Abren cerraduras sencillas.',
 "Dungeoneer's Pack":'Equipo completo para explorar cuevas.',
 "Explorer's Pack":'Equipo completo para viajes largos.',
 "Filcher's Pack":'Equipo completo para el que prefiere no ser visto.',
 'Egg Incubator':'Incuba huevos mientras caminas.',
 'Egg Incubator Plus':'Incubadora mejorada. Más rápida.',
 'Egg Incubator Super':'La mejor incubadora del mercado.',
 'Gimmighoul Coin':'Moneda antigua. Se coleccionan.',
 'Black Augurite':'Mineral negro y afilado. Provoca una evolución.',
 'Peat Block':'Bloque de turba antigua. Provoca una evolución.',
 'Auspicious Armor':'Armadura cargada de buena fortuna.',
 'Malicious Armor':'Armadura cargada de rencor.',
 'Cracked Pot':'Tetera agrietada. Provoca una evolución.',
 'Chipped Pot':'Tetera desportillada de gran valor.',
 'Unremarkable Teacup':'Taza corriente. Provoca una evolución.',
 'Masterpiece Teacup':'Taza de maestro, muy cotizada.',
 'Galarica Wreath':'Corona tejida con nueces de Galar.',
 'Metal Coat':'Recubrimiento metálico. Provoca una evolución.',
}

# bayas que reducen un tipo
RESIST = {'Occa':'fuego','Passho':'agua','Wacan':'eléctrico','Rindo':'planta','Yache':'hielo',
 'Chople':'lucha','Kebia':'veneno','Shuca':'tierra','Coba':'volador','Payapa':'psíquico',
 'Tanga':'bicho','Charti':'roca','Kasib':'fantasma','Haban':'dragón','Colbur':'siniestro',
 'Babiri':'acero','Chilan':'normal','Roseli':'hada'}
BAYAS = {'Cheri':'Cura la parálisis al comerla.','Chesto':'Despierta al que la come.',
 'Pecha':'Cura el envenenamiento.','Rawst':'Cura las quemaduras.','Aspear':'Descongela.',
 'Leppa':'Recupera usos de un movimiento.','Oran':'Restaura salud cuando esta baja.',
 'Persim':'Quita la confusión.','Lum':'Quita cualquier estado alterado.',
 'Sitrus':'Restaura bastante salud en apuros.'}

TIPOS_Z = {'Normalium':'normal','Fightinium':'lucha','Flyinium':'volador','Poisonium':'veneno',
 'Groundium':'tierra','Rockium':'roca','Buginium':'bicho','Ghostium':'fantasma',
 'Steelium':'acero','Firium':'fuego','Waterium':'agua','Grassium':'planta',
 'Electrium':'eléctrico','Psychium':'psíquico','Icium':'hielo','Draconium':'dragón',
 'Darkinium':'siniestro','Fairium':'hada'}

def describir(n):
    if n in D: return D[n]
    m = re.match(r'^(\w+) Berry$', n)
    if m:
        k = m.group(1)
        if k in BAYAS: return BAYAS[k]
        if k in RESIST: return f'Reduce el daño de un ataque supereficaz de tipo {RESIST[k]}.'
        return 'Baya que se consume para obtener su efecto.'
    m = re.match(r'^(\w+) Z$', n)
    if m and m.group(1) in TIPOS_Z:
        return f'Cristal Z de tipo {TIPOS_Z[m.group(1)]}. Potencia un movimiento una vez por combate.'
    if n.endswith(' Plate'):        return 'Placa antigua que refuerza los movimientos de su tipo.'
    if n.endswith(' Memory Disc'):  return 'Disco de memoria que cambia el tipo de Silvally.'
    if n.endswith(' Drive'):        return 'Casete que cambia el tipo del movimiento de Genesect.'
    if n.endswith(' Nectar'):       return 'Néctar que cambia la forma de Oricorio.'
    if n.endswith(' Candy'):        return 'Caramelo de entrenamiento: sube una característica.'
    if n.startswith('X '):          return 'Sube temporalmente una característica en combate.'
    return 'Objeto de Nubia.'

# ---------------------------------------------------------------- parseo
lineas = [l.strip() for l in LISTA.split('\n') if l.strip()]
i = lineas.index('Cost') + 1 if 'Cost' in lineas else 0
grupos, vistos = {}, set()
while i + 2 < len(lineas) + 1:
    try:
        nom, tipo, coste = lineas[i], lineas[i+1], lineas[i+2]
    except IndexError:
        break
    i += 3
    if tipo not in CAT:
        continue
    if nom in vistos:
        continue
    vistos.add(nom)
    precio = int(coste.replace('₽', '').replace(',', '')) if coste.strip() not in ('-', '') else 0
    grupos.setdefault(CAT[tipo], []).append((nom, precio, describir(nom)))

grupos['Llaves de Nubia'] = [
 ('Carta Náutica', 0, 'Abre el acceso a la Caverna del Cauca.'),
 ('Muestra de la Veta', 0, 'Abre el acceso al Ojo del Cañón.'),
 ('Permiso de la Federación', 0, 'Autoriza la subida al Camino Victoria.'),
 ('Balsa Dorada', 0, 'Plano en miniatura de la Sierra Nevada.'),
 ('Vueltiao de Rosalba', 0, 'Tejido que marca un camino que no está en los mapas.'),
 ('Pase del Teleférico', 0, 'Acceso a la estación alta de Ciudad Brisamar.'),
]

esc = lambda t: t.replace('\\', '\\\\').replace("'", "\\'")
out = ['const CATALOGO = {']
for cat in ORDEN:
    if cat not in grupos: continue
    out.append(f" '{cat}': [")
    for n, p, d in grupos[cat]:
        out.append(f"  ['{esc(n)}',{p},'{esc(d)}'],")
    out[-1] = out[-1][:-1]
    out.append(' ],')
out[-1] = out[-1][:-1]
out.append('};')

io.open('catalogo.js', 'w', encoding='utf-8').write('\n'.join(out))
total = sum(len(v) for v in grupos.values())
print(f'{total} objetos en {len(grupos)} categorías')
for c in ORDEN:
    if c in grupos: print(f'  {c:24s} {len(grupos[c])}')
genericas = sum(1 for v in grupos.values() for x in v if x[2] == 'Objeto de Nubia.')
print(f'sin descripción propia: {genericas}')
