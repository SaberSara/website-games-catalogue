#!/usr/bin/env python3
"""Reproducible K–12 resource expansion, October 2026.  Official source links are
manually researched; editorial topic associations are suggestions, NOT certification.
Works only on original seed records; idempotently replaces our additions on rerun.
"""
from pathlib import Path
import json, collections
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'data/games.json').read_text(encoding='utf-8'))
C=json.loads((ROOT/'data/curriculum.json').read_text(encoding='utf-8'))
TOPICS=C['topics']; SUBJECTS={'ela':'reading','math':'math','science':'science','hss':'world','arts':'arts','health':'health','pe':'move','cs':'coding'}
DATE='2026-10-15'
new=[]

def relevant_topic_ids(grades,subjects,matching=None):
    # Only add topics that really bear on the activity (exact editorial keywords), never filler.
    if not matching: return []
    ids=[]
    for gr in grades:
        patterns=matching.get(gr, matching.get('*', [])) if isinstance(matching,dict) else matching
        if isinstance(patterns,str):patterns=[patterns]
        for t in TOPICS:
            if t['grade']==gr and t['subject'] in subjects and any(x.casefold() in t['title'].casefold() for x in patterns):
                if t['id'] not in ids: ids.append(t['id'])
    return ids

def record(id,title,publisher,url,subjects,grades,description,kind='Interactive simulation',key=None,approved=True,ad_url=None,source_ids=None,notes='',platform='browser',access=None,price='Free',devices=None,learning=None,featured=False):
    if not isinstance(subjects,list): subjects=[subjects]
    if not isinstance(grades,list): grades=[str(x) for x in grades]
    grades=[str(x) for x in grades]
    assert not any(g['id']==id for g in new),id
    evidence=ad_url if approved else None
    review={'status':'publisher_claim_reviewed' if approved else 'needs_review', 'reviewedOn':DATE,
        'method':'Publisher policy and official destination review; no hands-on gameplay audit' if approved else 'Publisher game page found; no sufficiently scoped no-ad claim confirmed',
        'runtimeTested':False,'evidenceScope':'Official publisher-hosted resource. Check linked external content separately.',
        'notes':notes or ('No external runtime/device play-test completed.' if approved else 'Adult must check actual gameplay, ads, third-party redirects and requirements.')}
    if evidence: review['adEvidenceUrl']=evidence
    rec={'id':id,'title':title,'publisher':publisher,'url':url,'subjects':subjects,'grades':grades,
      'topicIds':relevant_topic_ids(grades,subjects,key),'kind':kind,'platform':platform,
      'access':access or ('Browser · adult guidance as needed' if approved else 'Browser · review account/access needs'),
      'priceLabel':price,'description':description,'art':SUBJECTS[subjects[0]],
      'thumbnailAsset':'subject-'+SUBJECTS[subjects[0]]+'.webp',
      'sourceIds':source_ids or [],'learningSuggestion':learning or 'Try one activity and discuss what you discovered.',
      'alignmentStatus':'Editorial grade/topic suggestion; not independently certified or a mastery assessment',
      'review':review,'featured':featured,'devices':devices or (['browser'] if platform=='browser' else ['ios','android'])}
    new.append(rec)

PHET='https://phet.colorado.edu/en/privacy-policy'
CODE='https://studio.code.org/terms-and-privacy'
KHAN='https://www.khanacademy.org/about/privacy-policy'
STAR='https://teach.starfall.com/privacy'

def phet_math(slug,title,gr,match,desc):
    record('phet-'+slug,title,'PhET Interactive Simulations','https://phet.colorado.edu/en/simulations/'+slug,'math',gr,desc,
    key=match,ad_url=PHET,source_ids=['phet-policy'],notes='Publisher prohibits advertising on PhET-hosted simulations. Free browser simulation, not necessarily a scored game; selected device/browser still needs testing.',
    access='Browser simulation · no student login',learning='Experiment with the model; explain one number pattern you notice.')

math_sims=[
# Slug, title, grade suggestion, topic title matching, concise learning focus
('number-play','Number Play',['K','1'],['Count','Number','Add'],'Play with quantities and count objects.'),
('number-compare','Number Compare',['K','1','2'],['More, fewer','Number','Place value'],'Compare numbers with visual models.'),
('number-pairs','Number Pairs',['K','1','2'],['Ways to make','Adding','Add & subtract'],'Find number pairs that work together.'),
('make-a-ten','Make a Ten',['K','1','2'],['Ways to make','number strategies','Add & subtract'],'Build combinations that total ten.'),
('fraction-matcher','Fraction Matcher',['2','3','4','5'],['equal parts','Fractions','Fraction operations'],'Match fractions shown in different ways.'),
('fractions-intro','Fractions: Intro',['2','3','4','5'],['equal parts','Fractions','Fraction operations'],'Explore fractions with shapes and numbers.'),
('build-a-fraction','Build a Fraction',['2','3','4','5'],['equal parts','Fractions','Fraction operations'],'Build matching fractions with pieces.'),
('fractions-equality','Fractions: Equality',['3','4','5','6'],['Fractions','Fraction operations','Integers and fractions'],'See when two fractions are equivalent.'),
('fractions-mixed-numbers','Fractions: Mixed Numbers',['4','5','6'],['Fractions','Fraction operations','Integers and fractions'],'Turn fractions into mixed numbers.'),
('area-model-introduction','Area Model: Introduction',['3','4','5'],['Area','Multi-digit','fraction operations'],'Explore multiplication using rectangles.'),
('area-model-multiplication','Area Model: Multiplication',['3','4','5','6'],['Multiply','Multi-digit','patterns and expressions','Expressions'],'Model multiplication with area.'),
('area-model-decimals','Area Model: Decimals',['4','5','6','7'],['Decimals','Place value','Integers and fractions','Rational numbers'],'Multiply and divide decimals visually.'),
('area-model-algebra','Area Model: Algebra',['7','8','9','10'],['Expressions','linear equations','Algebra'],'Make algebra expressions with area models.'),
('ratio-and-proportion','Ratio and Proportion',['6','7','8'],['Ratios','proportions','functions'],'Explore ratios by changing ingredients and sizes.'),
('unit-rates','Unit Rates',['6','7'],['Ratios','proportions'],'Compare rates and ratios.'),
('number-line-operations','Number Line: Operations',['2','3','4','5','6','7'],['Add','Multiply','fractions','integers','rational numbers','multi-digit'],'Explore addition and subtraction on a line.'),
('number-line-distance','Number Line: Distance',['3','4','5','6','7'],['Measurement','Graphs','Integers','rational numbers','patterns in data'],'See the distance between numbers.'),
('function-builder','Function Builder',['7','8','9','10','11','12'],['Expressions','functions'],'Discover input-output rules.'),
('function-builder-basics','Function Builder: Basics',['6','7','8'],['Patterns','Expressions','functions'],'Guess the rule inside a function machine.'),
('graphing-quadratics','Graphing Quadratics',['9','10','11','12'],['functions','algebra'],'Explore how quadratic graphs change.'),
('graphing-slope-intercept','Graphing Slope-Intercept',['7','8','9','10'],['Expressions','linear equations','functions'],'Make straight lines with slope and intercept.'),
('expression-exchange','Expression Exchange',['6','7','8','9'],['Expressions','linear equations','algebra'],'Trade equivalent algebra expressions.'),
('plinko-probability','Plinko Probability',['7','8','9','10','11','12'],['Probability','sampling','data','Statistics'],'Explore probability through bouncing balls.'),
('mean-share-and-balance','Mean: Share and Balance',['4','5','6','7'],['Data','Statistics','Sampling'],'Understand the average as fair sharing.'),
('center-and-variability','Center and Variability',['6','7','8','9'],['Statistics','data','Probability'],'Explore averages and spread in datasets.'),
('quadrilateral','Quadrilateral',['3','4','5','6','7'],['Area','Angles','Geometry','Shape'],'Build and compare four-sided shapes.'),
('proportion-playground','Proportion Playground',['6','7','8'],['Ratios','proportions','geometry'],'Play with scale and proportional relationships.'),
('trig-tour','Trig Tour',['10','11','12'],['geometry','functions'],'Explore trigonometry and special angles.'),
('least-squares-regression','Least-Squares Regression',['9','10','11','12'],['statistics','modelling'],'Fit lines to data points.'),
('equality-explorer','Equality Explorer',['6','7','8','9'],['Expressions','linear equations','algebra'],'Balance equations by changing both sides.'),
('curve-fitting','Curve Fitting',['9','10','11','12'],['statistics','modelling','functions'],'Fit curves to experimental data.'),
('calculus-grapher','Calculus Grapher',['11','12'],['functions','modelling'],'Explore slopes, areas and functions (optional extension).'),
]
for x in math_sims:phet_math(*x)

def phet_science(slug,title,gr,match,desc):
    record('phet-'+slug,title,'PhET Interactive Simulations','https://phet.colorado.edu/en/simulations/'+slug,'science',gr,desc,
    key=match,ad_url=PHET,source_ids=['phet-policy'],notes='Publisher no-ad policy applies to its own website/simulations. Intro or enrichment grade suggestions are editorial; browser compatibility not play-tested.',
    access='Browser simulation · no student login',learning='Change one variable and predict what will happen next.')

science_sims=[
('forces-and-motion-basics','Forces and Motion: Basics',['3','4','8','9','10'],['Forces','Energy','motion'],'Explore pushing, pulling, friction and motion.'),
('balancing-act','Balancing Act',['3','4','6'],['Forces','Energy','engineering'],'Experiment with balance and forces.'),
('states-of-matter-basics','States of Matter: Basics',['2','5','7','9','10'],['Materials','Matter','atoms'],'Heat and cool particles to see state changes.'),
('color-vision','Color Vision',['1','4','8','9'],['Light','Waves'],'Mix light and explore what we see.'),
('waves-intro','Waves: Intro',['1','4','8','9'],['Sound','Waves'],'Play with waves, frequency and amplitude.'),
('masses-and-springs-basics','Masses and Springs: Basics',['4','8','9'],['Energy','Forces'],'Explore springs, motion and energy.'),
('energy-skate-park-basics','Energy Skate Park: Basics',['4','6','8','9','10'],['Energy','forces'],'Watch how energy changes on a skate track.'),
('gravity-and-orbits','Gravity and Orbits',['5','8','9','10','11','12'],['Space','Earth','forces'],'Explore gravitational pull and orbital motion.'),
('greenhouse-effect','Greenhouse Effect',['3','6','7','9','10','11','12'],['Weather','Earth','resources','ecosystems'],'Explore how Earth retains heat.'),
('natural-selection','Natural Selection',['3','6','8','9','10','11','12'],['Ecosystems','Evolution','traits'],'Investigate how populations change over time.'),
('gene-expression-essentials','Gene Expression Essentials',['6','8','9','10','11','12'],['Cells','organisms','Evolution','ecosystems'],'Explore how genes influence proteins and traits.'),
('circuit-construction-kit-dc','Circuit Construction Kit: DC',['4','8','9','10','11','12'],['Energy','Waves','technology','engineering'],'Build and test electrical circuits.'),
('wave-interference','Wave Interference',['4','8','9','10','11','12'],['Waves','technology'],'See how waves overlap and interfere.'),
('gas-properties','Gas Properties',['5','7','9','10','11','12'],['Matter','atoms'],'Change temperature, pressure and volume.'),
('density','Density',['2','5','7','9','10','11','12'],['Materials','Matter','atoms'],'Explore which objects float and sink.'),
('gravity-force-lab-basics','Gravity Force Lab: Basics',['5','8','9','10','11','12'],['Space','Earth','forces'],'Change masses and measure gravitational forces.'),
('my-solar-system','My Solar System',['5','8','9','10','11','12'],['Space','Earth'],'Experiment with orbital paths.'),
('molecule-shapes-basics','Molecule Shapes: Basics',['7','9','10','11','12'],['Matter','atoms'],'Build molecules and explore their shapes.'),
('reactants-products-and-leftovers','Reactants, Products and Leftovers',['5','7','9','10','11','12'],['Matter','reactions','atoms'],'Balance reactions with ingredients and molecules.'),
('ph-scale-basics','pH Scale: Basics',['5','7','9','10','11','12'],['Matter','reactions','atoms'],'Explore acidity and alkalinity.'),
('molarity','Molarity',['9','10','11','12'],['Matter','atoms'],'Mix solutions and compare concentrations.'),
('projectile-motion','Projectile Motion',['8','9','10','11','12'],['Forces','motion','energy'],'Explore launch angle, speed and trajectory.'),
('bending-light','Bending Light',['4','8','9','10','11','12'],['Waves','light','technology'],'See how light refracts and reflects.'),
('ohms-law','Ohm’s Law',['8','9','10','11','12'],['Energy','Waves','technology'],'Explore current, voltage and resistance.'),
('energy-forms-and-changes','Energy Forms and Changes',['4','6','8','9','10','11','12'],['Energy','ecosystems'],'Follow energy as it flows and changes.'),
('coulombs-law','Coulomb’s Law',['8','9','10','11','12'],['Forces','energy'],'Investigate the forces between charges.'),
('faradays-law','Faraday’s Law',['8','9','10','11','12'],['Energy','Waves','technology'],'Explore electromagnetism and induction.'),
('blackbody-spectrum','Blackbody Spectrum',['9','10','11','12'],['Waves','technology'],'Explore light colour and temperature.'),
('atomic-interactions','Atomic Interactions',['9','10','11','12'],['Matter','atoms'],'Explore forces between atoms.'),
('charges-and-fields','Charges and Fields',['9','10','11','12'],['Forces','energy','technology'],'Build electric field patterns.'),
('beers-law-lab','Beer’s Law Lab',['9','10','11','12'],['Matter','atoms','waves'],'Use light to measure solution concentration.'),
('isotopes-and-atomic-mass','Isotopes and Atomic Mass',['9','10','11','12'],['Matter','atoms'],'Explore isotopes and atomic masses.'),
]
for x in science_sims:phet_science(*x)

# Official Code.org destinations; publisher's services prohibit advertising.
def code(id,title,url,gr,desc,topics,kind='Game adventure',subjects=None,notes='',access='Browser · some classroom courses ask for a login'):
    record('codeorg-'+id,title,'Code.org',url,subjects or 'cs',gr,desc,kind=kind,key=topics,
      approved=True,ad_url=CODE,price='Free',access=access,
      notes=notes or 'Code.org prohibits advertising on its services. Official destination is a course/tool; individual levels and sign-in requirements need hands-on review.',
      learning='Create, debug or explain the program you made.')

for slug,letter,gr,sub in [
('coursea','A',['K'],'Beginner coding puzzles'),('courseb','B',['1'],'Early logic and sequences'),
('coursec','C',['2'],'Loops and digital stories'),('coursed','D',['3'],'Patterns and loops'),
('coursee','E',['4'],'Algorithms and problem solving'),('coursef','F',['5'],'Coding projects and creativity')]:
    code(slug,'Coding Course '+letter,'https://studio.code.org/s/'+slug,gr,sub,
    ['steps','algorithms'],'Activity collection',access='Browser course · sign-in may be offered')
code('sprite-lab','Sprite Lab','https://studio.code.org/projects/spritelab/new',['3','4','5','6','7','8'],
     'Make animated characters and interactive stories.',['algorithms','programming','create','perform'],
     kind='Creative tool',subjects=['cs','arts'],access='Browser editor · project saving may ask for sign-in')
code('artist','Artist Drawing','https://studio.code.org/projects/artist/new',['2','3','4','5'],
     'Use code to draw paths and patterns.',['algorithms','create'],kind='Creative tool',subjects=['cs','arts'])
code('dance','Dance Party','https://code.org/en-US/hour-of-code/dance',['2','3','4','5','6','7','8','9','10','11','12'],
     'Code an animated dance to music.',['algorithms','create','perform'],kind='Game adventure',subjects=['cs','arts'],
     notes='Official Code.org no-ad policy. Some songs feature commercial music; review age-appropriateness and sound requirements.')
code('music-lab','Music Lab','https://code.org/en-US/tools/music-lab',['6','7','8','9','10','11','12'],
     'Make interactive music with code blocks.',['algorithms','create','perform'],kind='Creative tool',subjects=['cs','arts'],
     notes='Publisher forbids ads on its services. Uses licensed music and may ask a learner to sign in to save work.')
code('cs-discoveries','CS Discoveries','https://code.org/en-US/curriculum/computer-science-discoveries',['6','7','8','9','10'],
     'Build games, animations and simple websites.',['algorithms','programming','data','society'],kind='Activity collection',
     notes='This is a teacher/curriculum landing with learner activity links; some tasks require classroom setup. Publisher lists Grades 6–10.')
code('cs-principles','CS Principles','https://code.org/en-US/curriculum/computer-science-principles',['9','10','11','12'],
     'Explore creative coding, data and the internet.',['algorithms','data','society'],kind='Activity collection',
     notes='AP-aligned school course with project challenges, not a single launchable game. Some units require a classroom/account.')
code('cs-fundamentals','CS Fundamentals','https://code.org/en-US/curriculum/computer-science-fundamentals',['K','1','2','3','4','5'],
     'Explore colorful coding puzzles for young learners.',['steps','algorithms'],kind='Activity collection',
     notes='Course selection page, not a standalone game; many puzzles can be used without signing in.')

# Khan Academy: interactive practice rather than game.  No third-party ads per policy;
# may show separately labeled sponsorship or subscription feature links. State scope honestly.
def khan(id,title,url,subject,gr,desc,matches):
    record('khan-'+id,title,'Khan Academy',url,subject,gr,desc,kind='Activity collection',key=matches,
      ad_url=KHAN,price='Free learning activities',
      access='Browser · some exercises may prompt a learner account',
      notes='Khan Academy policy forbids third-party advertisements but may show labeled sponsorship or supporter messages. Not a promotion-free guarantee; practice and videos are not mini-games.',
      learning='Complete a short exercise, then explain your answer or idea.')

khan('math2','2nd Grade Math','https://www.khanacademy.org/math/cc-2nd-grade-math','math',['2'],
 'Practise place value, sums and shapes.',['add','place value','equal groups','measure','time','shapes'])
khan('math3','3rd Grade Math','https://www.khanacademy.org/math/cc-third-grade-math','math',['3'],
 'Practise multiplication, fractions and area.',['multiply','fractions','area','time'])
khan('math4','4th Grade Math','https://www.khanacademy.org/math/cc-fourth-grade-math','math',['4'],
 'Explore fractions, decimals and angles.',['multi-digit','factors','fractions','decimals','angles'])
khan('math5','5th Grade Math','https://www.khanacademy.org/math/cc-fifth-grade-math','math',['5'],
 'Build skills in fractions, decimals and volume.',['place value','fraction','volume','coordinate'])
khan('math6','6th Grade Math','https://www.khanacademy.org/math/cc-sixth-grade-math','math',['6'],
 'Practise ratios, equations and statistics.',['ratio','integer','expression','statistics'])
khan('math7','7th Grade Math','https://www.khanacademy.org/math/cc-seventh-grade-math','math',['7'],
 'Solve problems with ratios and rational numbers.',['ratio','rational','expression','probability'])
khan('math8','8th Grade Math','https://www.khanacademy.org/math/cc-eighth-grade-math','math',['8'],
 'Explore linear equations, functions and geometry.',['linear','functions','Pythagorean','transformations'])
khan('algebra','Algebra Practice','https://www.khanacademy.org/math/algebra','math',['8','9','10','11','12'],
 'Practise algebraic expressions and equations.',['equations','algebra'])
khan('geometry','Geometry Practice','https://www.khanacademy.org/math/geometry','math',['9','10','11','12'],
 'Explore geometry with interactive problems.',['geometry'])
khan('statistics','Statistics & Probability','https://www.khanacademy.org/math/statistics-probability','math',['9','10','11','12'],
 'Explore data and probability with exercises.',['statistics'])
khan('ela2','Reading & Vocabulary — Grade 2','https://www.khanacademy.org/ela/cc-2nd-reading-vocab','ela',['2'],
 'Read short texts and practise vocabulary.',['informational','vocabulary','stories'])
khan('ela3','Reading & Vocabulary — Grade 3','https://www.khanacademy.org/ela/cc-3rd-reading-vocab','ela',['3'],
 'Build vocabulary and understand passages.',['informational','vocabulary','stories'])
khan('ela4','Reading & Vocabulary — Grade 4','https://www.khanacademy.org/ela/4th-grade-reading-and-vocab','ela',['4'],
 'Discover words and read for meaning.',['informational','vocabulary','stories'])
khan('ela56grammar','Grammar — Grades 5–6','https://en.khanacademy.org/ela/5th-and-6th-grade-grammar','ela',['5','6'],
 'Explore sentence grammar with practice.',['vocabulary','writing'])
khan('ela7','Reading & Vocabulary — Grade 7','https://www.khanacademy.org/ela/7th-grade-reading-and-vocabulary','ela',['7'],
 'Read complex texts and discover new words.',['informational','vocabulary','stories'])
khan('ela9','Reading & Vocabulary — Grade 9','https://www.khanacademy.org/ela/9th-grade-reading-and-vocabulary','ela',['9'],
 'Explore evidence, ideas and word meanings.',['informational','vocabulary','stories'])
khan('ela10','Reading & Vocabulary — Grade 10','https://www.khanacademy.org/ela/10th-grade-reading-and-vocabulary','ela',['10'],
 'Improve comprehension and close reading.',['informational','vocabulary','stories'])
khan('ela-grammar','Grammar Practice','https://www.khanacademy.org/humanities/grammar','ela',['8','9','10','11','12'],
 'Practise sentences, punctuation and usage.',['vocabulary','writing'])
khan('us-history','US History — Explore','https://www.khanacademy.org/humanities/us-history','hss',['8','11','12'],
 'Explore history through resources and questions.',['founding','reconstruction','industry','war','civil rights','modern','government'],)
khan('world-history','World History — Explore','https://www.khanacademy.org/humanities/world-history','hss',['6','7','10'],
 'Explore civilizations and global history.',['ancient','medieval','revolutions','world wars','global'])
khan('art-history','Art History — Explore','https://www.khanacademy.org/humanities/art-history','arts',['6','7','8','9','10','11','12'],
 'Explore artworks and creative ideas.',['respond','connect'])

# Starfall explicitly no ads; landing pages may include supporter-only extras.
record('starfall-grade2-math','Starfall: Grade 2 Math','Starfall','https://www.starfall.com/h/math2/','math',['2'],
       'Play with place value and addition.',kind='Activity collection',key=['place value','add','equal groups'],
       ad_url=STAR,source_ids=['starfall-privacy'],price='Free selections · member extras',
       notes='Official Grade 2 collection contains free and supporter/member-only activities, clearly indicated on source page. No third-party advertising, not universally free.')
record('starfall-grade3-math','Starfall: Grade 3 Math','Starfall','https://www.starfall.com/h/math3/','math',['3'],
       'Explore multiplication, fractions and area.',kind='Activity collection',key=['multiply','fractions','area'],
       ad_url=STAR,source_ids=['starfall-privacy'],price='Free selections · member extras',
       notes='Includes free and member-only games. Publisher says Starfall has no ads. Grade 3 math learning collection.')
for id,title,url,gr,match,desc in [
('starfall-wacky-house','Wacky House: Perimeter','https://www.starfall.com/h/measure/wacky-house/',['3'],['area','perimeter'],'Explore perimeter while building a house.'),
('starfall-pumpkin-fractions','Pumpkin Fractions','https://www.starfall.com/h/multdiv/pumpkin-fractions/?sn=math3',['3'],['fractions'],'Place fractions on a number line.'),
('starfall-robot-fractions','Robot Fraction Shapes','https://www.starfall.com/h/multdiv/robot-shapes/',['3'],['fractions'],'Match equivalent fractions with robots.'),
('starfall-fraction-aliens','Alien Planet Fractions','https://www.starfall.com/h/multdiv/alienplanet/',['3'],['fractions'],'Compare fractions with friendly aliens.'),
]:
    record(id,title,'Starfall',url,'math',gr,desc,kind='Mini-game',key=match,ad_url=STAR,
     source_ids=['starfall-privacy'],price='Free / check activity',notes='Publisher grade 3 curriculum guide lists this direct activity; confirm supporter restrictions in live gameplay before public rollout.')

# More promising options: no exact-page claim confirming no ads; hide until adult audit.
for slug,title,gr,desc,match in [
('Song-Maker','Song Maker',['K','1','2','3','4','5','6','7','8'],'Build little songs by placing coloured blocks.',['music','create']),
('Rhythm','Rhythm',['K','1','2','3','4'],'Play with beats and patterns.',['music','create']),
('Kandinsky','Kandinsky',['K','1','2','3','4'],'Turn pictures into sounds.',['music','create']),
('Spectrogram','Spectrogram',['4','5','6','7','8','9','10','11','12'],'See what sound frequencies look like.',['music','waves','respond']),
('Arpeggios','Arpeggios',['4','5','6','7','8','9'],'Experiment with chord patterns.',['music','create']),
('Chords','Chords',['3','4','5','6','7','8'],'Make and compare musical chords.',['music','create']),
]:
    record('chrome-music-'+slug.lower(),title,'Chrome Music Lab','https://musiclab.chromeexperiments.com/'+slug+'/','arts',gr,
     desc,kind='Creative tool',key=match,approved=False,price='Free',
     notes='No explicit current no-ad promise verified for the exact tool; publisher and cookies/device experience require adult review.')

# Official iCivics and Mission US games; reviewed for topic, not advertising or account experience.
for slug,title,gr,desc,match in [
('branches-of-power','Branches of Power',['8','11','12'],'Run all three branches of US government.',['founding','government','democracy','constitution']),
('do-i-have-a-right','Do I Have a Right?',['8','11','12'],'Run a law office and explore constitutional rights.',['founding','constitution','rights']),
('lawcraft','LawCraft',['8','11','12'],'Guide a bill through Congress.',['founding','government','civic']),
('newsfeed-defenders','NewsFeed Defenders',['6','7','8','9','10','11','12'],'Spot misleading posts and hidden advertisements.',['citizen','society','government','modern']),
('cast-your-vote','Cast Your Vote',['8','11','12'],'Explore voting decisions and questions.',['founding','government','democracy']),
('constitutional-compromise','Constitutional Compromise',['5','8','11','12'],'Explore the choices behind the Constitution.',['Constitution','founding']),
('race-to-ratify','Race to Ratify',['5','8','11','12'],'Experience the debate over the Constitution.',['Constitution','founding']),
('peoples-pie','People’s Pie',['8','11','12'],'Explore tradeoffs in budgeting.',['econom','government']),
('counties-work','Counties Work',['6','8','11','12'],'Manage public services for a county.',['citizen','government','econom']),
]:
   record('icivics-'+slug,title,'iCivics','https://www.icivics.org/games/'+slug,'hss',gr,desc,
     kind='Game adventure',key=match,approved=False,price='Free / verify',
     notes='Official iCivics game catalogue lists this title. External account, ads, rights notices and game runtime require adult verification.')
for id,title,gr,desc,match in [
('for-crown-or-colony','For Crown or Colony?',['5','8'],'Experience a story from colonial America.',['colonization','founding']),
('a-cheyenne-odyssey','A Cheyenne Odyssey',['5','8'],'Explore a Cheyenne family’s experiences.',['Indigenous','expansion']),
('up-from-the-dust','Up from the Dust',['8','11'],'Experience Dust Bowl-era choices.',['industry','depression']),
('prisoner-in-my-homeland','Prisoner in My Homeland',['11'],'Explore Japanese American incarceration.',['war','rights']),
('no-turning-back','No Turning Back',['11'],'Explore the civil rights movement through a story.',['civil rights']),
]:
    record('mission-us-'+id,title,'Mission US','https://www.mission-us.org/play/','hss',gr,desc,
      kind='Game adventure',key=match,approved=False,price='Free / verify',
      notes='Mission US interactive narrative selection page. Publisher recommends that educators pre-screen sensitive history; age/topic appropriateness, exact deep link and ad experience need adult checks.')

# Enrich existing Khan Academy Kids grade eligibility only if publisher supports age 2-8.
for g in D['games']:
    if g['id']=='khan-kids' and '2' not in g['grades']:
        g['grades'].append('2')
        g['topicIds'].extend(relevant_topic_ids(['2'],['ela','math','health'],['word reading','add','wellbeing']))
        g['review']['notes']+=' Publisher describes ages 2–8 / pre-K through second grade; Grade 2 added as younger-learner option.'

D['games']=[g for g in D['games'] if not g['id'].startswith(('codeorg-','chrome-music-','icivics-','mission-us-','khan-math','khan-ela','khan-algebra','khan-geometry','khan-statistics','khan-us-history','khan-world-history','khan-art-history')) and not (g['id'].startswith('phet-') and g['id'] not in ['phet-equality-explorer-basics','phet-area-builder','phet-number-line-integers','phet-graphing-lines','phet-build-an-atom']) and not g['id'].startswith('starfall-grade') and not g['id'].startswith(('starfall-wacky','starfall-pumpkin','starfall-robot','starfall-fraction'))]+new
D['policy']='Child preview includes only games with a scoped publisher no-third-party-ads or no-ad policy. Khan Academy may show labeled sponsorships. This is publisher documentation, not runtime ad certification. Unsure links remain adult-only.'
D['reviewedOn']=DATE
D['seedRevision']=2
(ROOT/'data/games.json').write_text(json.dumps(D,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

coverage=collections.defaultdict(lambda:collections.Counter())
for g in D['games']:
 if g['review']['status']!='publisher_claim_reviewed': continue
 for grade in g['grades']:
  for subject in g['subjects']:coverage[grade][subject]+=1
print('Seed 28 + Added',len(new),'=',len(D['games']))
print('Approved:',sum(g['review']['status']=='publisher_claim_reviewed' for g in D['games']))
for gr in ['K']+[str(x) for x in range(1,13)]:
 print(gr,'visible',sum(coverage[gr].values()),'by subject',dict(coverage[gr]))
print('New entries lacking topic match: ',[(g['id'],g['grades']) for g in new if not g['topicIds']][:20], 'total',sum(not g['topicIds'] for g in new))
