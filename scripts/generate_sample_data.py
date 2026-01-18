#!/usr/bin/env python3
"""Generate sample data files for testing the knowledge retrieval chatbot."""

import os
import subprocess
import tempfile

LOCAL_DIR = "example-data/local"
GITHUB_DIR = "example-data/github"

# Content templates - cute topics with varying sizes

SMALL_MD_CONTENT = [
    # Small level 1 sections - fit within semantic chunk
    """# Persian Cat Care Guide

Persian cats are known for their luxurious long coats and sweet personalities. They require daily grooming to prevent matting and regular eye cleaning due to their flat faces. These gentle cats prefer calm environments and make excellent indoor companions.
""",
    """# Golden Retriever Puppies

Golden Retriever puppies are bundles of joy with their fluffy golden coats and playful nature. They're known for being friendly, intelligent, and eager to please. Early socialization and training helps them grow into well-mannered adult dogs.
""",
    """# Sunflower Growing Tips

Sunflowers are cheerful flowers that turn their heads to follow the sun. Plant seeds directly in the ground after the last frost. They need full sun and well-drained soil. Most varieties grow 6-12 feet tall and bloom in mid to late summer.
""",
    """# Holland Lop Bunnies

Holland Lop bunnies are adorable small rabbits with floppy ears and compact bodies. They weigh only 2-4 pounds and have sweet, gentle temperaments. These bunnies love to play and can be litter trained.
""",
    """# Butterfly Garden Basics

Create a butterfly garden by planting nectar-rich flowers like zinnias, coneflowers, and butterfly bush. Include host plants for caterpillars. Butterflies need sunny spots and shallow water sources. Avoid pesticides to keep them safe.
""",
    """# Hamster Happiness

Hamsters are adorable pocket pets that love to run on wheels and stuff their cheeks with food. Syrian hamsters should live alone while dwarf hamsters can sometimes live in pairs. Provide plenty of bedding for burrowing.
""",
    """# Kitten Playtime

Kittens need lots of playtime to develop properly. Interactive toys like feather wands and laser pointers stimulate their hunting instincts. Play sessions of 15-20 minutes several times a day keep kittens happy and healthy.
""",
    """# Tulip Varieties

Tulips come in nearly every color of the rainbow. Popular varieties include Darwin hybrids for their large blooms, parrot tulips for their feathery petals, and lily-flowered tulips for their elegant pointed petals.
""",
    """# Guinea Pig Sounds

Guinea pigs communicate through adorable sounds. Wheeking means they're excited, usually about food. Purring indicates contentment. Popcorning - jumping and twisting in the air - shows pure joy and happiness.
""",
    """# Lavender Benefits

Lavender is a fragrant purple flower loved by bees and butterflies. Its calming scent is used in aromatherapy for relaxation. Dried lavender can be used in sachets, and the flowers are edible in small amounts.
""",
    """# Cockatiel Personality

Cockatiels are charming birds known for their whistling abilities and crest feathers that show their mood. When happy, their crest stands tall. They bond closely with their owners and can live 15-25 years.
""",
    """# Daisy Chain Making

Making daisy chains is a delightful summer activity. Pick daisies with long stems, use your fingernail to make a small slit in each stem, then thread the next daisy through. Connect the ends to make a crown or bracelet.
""",
    """# Pygmy Goat Facts

Pygmy goats are miniature goats that make wonderful pets. They're playful, curious, and love to climb on anything they can find. Despite their small size, they have big personalities and enjoy human companionship.
""",
    """# Rose Garden Care

Roses reward careful attention with stunning blooms. Water deeply at the base, avoiding wet leaves. Prune in early spring and deadhead spent blooms. Feed monthly during growing season for abundant flowers.
""",
    """# Hedgehog Habits

Hedgehogs are nocturnal cuties that curl into spiky balls when scared. They enjoy exploring and need exercise wheels in their enclosures. These insectivores eat special hedgehog food, mealworms, and some fruits.
""",
    """# Pansy Colors

Pansies bring cheerful faces to gardens with their distinctive markings. These cool-weather flowers come in purple, yellow, orange, red, and multicolored varieties. They're edible and make beautiful cake decorations.
""",
    """# Chinchilla Dust Baths

Chinchillas have incredibly soft fur that they keep clean with dust baths. They roll and flip in special volcanic dust, which absorbs oils and removes dirt. Watching a chinchilla dust bath is pure entertainment.
""",
]

LARGE_MD_CONTENT = [
    # Large level 1 sections with level 2 subsections for chunking
    """# Complete Guide to Maine Coon Cats

Maine Coon cats are one of the largest domesticated cat breeds, known as gentle giants of the feline world. These magnificent cats have captured hearts worldwide with their impressive size, tufted ears, and bushy tails.

## Physical Characteristics

Maine Coons are truly impressive cats. Males typically weigh 13-18 pounds, though some can reach 25 pounds or more. Females are smaller, usually 8-12 pounds. Their bodies are long and muscular, with broad chests and strong legs.

Their most distinctive features include large, tufted ears with lynx-like tips, and enormous, expressive eyes that can be green, gold, or copper. Their tails are incredibly long and fluffy, which they wrap around themselves for warmth. The coat is water-resistant and varies in length, being shorter on the shoulders and longer on the stomach and britches.

Maine Coons come in virtually every color and pattern except pointed patterns. Brown tabby is the most common and iconic color, but they also come in solid colors, bi-colors, and various tabby patterns.

## Personality and Temperament

Despite their imposing size, Maine Coons are known for their gentle, friendly personalities. They're often called "dog-like" because of their loyalty and tendency to follow their owners around the house. They're not typically lap cats, but they always want to be near their people.

Maine Coons are intelligent and playful well into adulthood. They enjoy interactive toys, puzzle feeders, and games of fetch. Many Maine Coons are fascinated by water and may play in their water bowls or join you near the bathtub.

They're generally good with children and other pets, making them excellent family cats. Their patient, laid-back nature means they tolerate handling well. They communicate with adorable chirps and trills rather than typical meows.

## Care Requirements

The luxurious Maine Coon coat requires regular maintenance. Brush them 2-3 times per week to prevent matting, paying special attention to the areas behind the ears and under the legs where tangles form easily. During shedding season in spring and fall, daily brushing may be necessary.

Maine Coons are generally healthy but can be prone to certain genetic conditions. Hip dysplasia is more common in Maine Coons than other cat breeds due to their large size. Hypertrophic cardiomyopathy (HCM) is another concern, so regular veterinary check-ups are important.

Due to their size, Maine Coons need larger litter boxes, cat trees, and beds than average cats. They're prone to obesity, so monitor their food intake and ensure they get plenty of exercise.

## History and Origin

Maine Coons are one of the oldest natural breeds in North America, originating in the state of Maine. Various folk tales explain their origins, including the genetically impossible story that they're descended from raccoons (hence the name "Coon").

The most likely explanation is that Maine Coons developed from matings between local short-haired domestic cats and long-haired cats brought by seafarers. Their thick coats and large, tufted paws evolved as adaptations to harsh New England winters.

Maine Coons were popular show cats in the late 1800s but nearly went extinct as Persian cats gained popularity. Dedicated breeders saved the breed, and Maine Coons have been growing in popularity since the 1980s.
""",
    """# The Joy of Labrador Retrievers

Labrador Retrievers have been America's most popular dog breed for decades, and for good reason. These versatile, friendly dogs excel as family pets, working dogs, and everything in between.

## Breed Overview

Labs are medium to large dogs, typically weighing 55-80 pounds. They have athletic, well-balanced bodies built for swimming and retrieving. Their short, dense double coat is water-resistant and comes in three colors: black, yellow, and chocolate.

Their most recognizable features include their broad heads with friendly, intelligent eyes, and their distinctive "otter tail" which is thick at the base and tapers to the tip. This tail acts as a powerful rudder when swimming.

Labs have webbed feet and a water-resistant coat, making them natural swimmers. Their soft mouths were bred to retrieve game birds without damaging them, which also makes them gentle when playing with children.

## Temperament

Labrador Retrievers are renowned for their friendly, outgoing personalities. They're eager to please and highly trainable, which is why they excel as service dogs, therapy dogs, and search-and-rescue dogs. Their gentle nature makes them wonderful family pets.

Labs are energetic and playful, maintaining their puppy-like enthusiasm well into adulthood. They need plenty of exercise and mental stimulation to prevent boredom. A bored Lab can become destructive, channeling their energy into chewing and digging.

These social dogs love everyone they meet, which makes them poor guard dogs but excellent companions. They thrive on human interaction and don't do well when left alone for long periods. Labs are generally good with children and other pets.

## Training and Exercise

Labs are highly trainable due to their intelligence and desire to please. They respond well to positive reinforcement training and excel in obedience, agility, and field trials. Early socialization and puppy training classes are recommended.

These active dogs need at least an hour of exercise daily. Swimming is an ideal activity for Labs, as it provides excellent exercise while being easy on their joints. They also enjoy fetch, hiking, and running alongside a bicycle.

Mental stimulation is equally important. Puzzle toys, training sessions, and interactive games keep Labs' minds engaged. Many Labs enjoy having a job to do, whether it's carrying items around the house or learning new tricks.

## Health Considerations

Labs are generally healthy dogs with a lifespan of 10-12 years. However, they're prone to certain health issues. Hip and elbow dysplasia are common in the breed, so buying from health-tested parents is important.

Labs have a tendency toward obesity because they love food and will eat anything. Portion control and regular exercise are essential. Obesity can lead to joint problems and other health issues.

Other concerns include exercise-induced collapse (EIC), progressive retinal atrophy (PRA), and ear infections. Regular veterinary check-ups and genetic testing can help manage these risks.

## Living with a Lab

Labs shed year-round with heavier shedding in spring and fall. Regular brushing helps manage shedding and keeps their coat healthy. They only need occasional baths unless they get into something messy.

These dogs need space to move and play. While they can adapt to apartment living with sufficient exercise, they're happiest with a yard to explore. A secure fence is important as Labs will follow their noses if they catch an interesting scent.

Labs are often described as perpetual puppies. Their enthusiastic, joyful approach to life brings smiles to everyone around them. With proper training, exercise, and love, a Labrador Retriever will be a devoted family member for years to come.
""",
    """# Creating a Cottage Garden

Cottage gardens are romantic, informal gardens overflowing with flowers, herbs, and charm. This style originated in English country villages where practical plants mingled with beautiful blooms.

## Design Principles

Cottage gardens have a seemingly haphazard appearance that actually requires careful planning. The key is controlled abundance - plants should look like they've self-seeded naturally while still allowing for maintenance and paths.

Use curved paths rather than straight lines. Paths can be made of flagstone, gravel, brick, or even grass. They should be wide enough to walk comfortably and should meander through the garden rather than cutting directly through.

Incorporate structural elements like arbors, trellises, and picket fences covered in climbing roses or clematis. A classic cottage garden might include a wooden bench, a birdbath, or a sundial as focal points. These structures provide vertical interest and support climbing plants.

## Plant Selection

Choose old-fashioned flowers with romantic appeal. Classic cottage garden plants include roses, delphiniums, hollyhocks, foxgloves, peonies, and lavender. Mix in herbs like rosemary, sage, and thyme for fragrance and practicality.

Layer plants by height, with tall plants like hollyhocks and delphiniums at the back, medium plants like roses and peonies in the middle, and low-growing plants like lavender and catmint at the front. This creates depth and allows all plants to be visible.

Include plants that self-seed, like foxgloves, sweet William, and forget-me-nots. These will naturalize throughout the garden, adding to the informal cottage feel. Allow some plants to sprawl over path edges for a softened look.

## Color Schemes

Traditional cottage gardens use soft, romantic colors: pinks, purples, blues, whites, and touches of yellow. However, you can create a cottage garden in any color scheme that appeals to you.

For a classic look, combine pink roses with purple lavender, blue delphiniums, and white daisies. For a more vibrant scheme, mix hot pinks, oranges, and reds. Monochromatic cottage gardens in all white or all pink are elegantly sophisticated.

Repeat colors throughout the garden to create unity. If you use purple in one area, include it in others as well. Foliage color matters too - silver-leaved plants like lamb's ear provide contrast and cool down bright colors.

## Seasonal Interest

Plan for flowers throughout the growing season. Early spring can feature tulips, daffodils, and bleeding hearts. Late spring brings irises, peonies, and roses. Summer offers the fullest display with delphiniums, lilies, and coneflowers.

Fall gardens can include asters, sedums, and chrysanthemums. Don't forget about foliage and structure - ornamental grasses add movement, and plants like Russian sage provide late-season color.

Include some evergreen elements like boxwood hedges or rosemary plants to provide winter interest. Rose hips, dried seed heads, and ornamental grasses can look beautiful covered in frost.

## Maintenance

Despite their wild appearance, cottage gardens need regular maintenance. Deadhead spent blooms to encourage continued flowering. Stake tall plants like delphiniums before they flop. Divide perennials every few years to maintain vigor.

Mulch beds to retain moisture and suppress weeds. Water deeply but infrequently to encourage deep root growth. Feed plants with compost or organic fertilizer in spring.

Allow some plants to set seed if you want them to self-sow. Edit ruthlessly - cottage gardens can become overgrown quickly. Remove plants that have become too aggressive or no longer earn their place.
""",
    """# Complete Rabbit Care Guide

Rabbits are delightful pets that bring joy with their curious personalities and adorable antics. Proper care ensures these gentle creatures live happy, healthy lives of 8-12 years.

## Housing Requirements

Indoor housing is safest for pet rabbits. A rabbit's living space should allow at least three to four hops in any direction - bigger is always better. Many rabbit owners use exercise pens or dedicate a bunny-proofed room.

The flooring should be solid, not wire, as wire can hurt rabbit feet and cause sore hocks. Line the area with hay, fleece blankets, or rabbit-safe mats. Include a hiding house where your rabbit can retreat when feeling stressed.

Litter boxes should be large enough for the rabbit to sit in comfortably. Use paper-based litter - never clumping cat litter or cedar shavings, which are dangerous for rabbits. Place hay near the litter box as rabbits like to eat while doing their business.

## Diet and Nutrition

Hay is the most important part of a rabbit's diet, making up about 80% of what they eat. Timothy hay is ideal for adult rabbits; alfalfa hay is only appropriate for young or underweight rabbits due to its high calcium content.

Fresh vegetables should be offered daily - about 2 cups of leafy greens per 6 pounds of body weight. Good options include romaine lettuce, cilantro, parsley, and bok choy. Introduce new vegetables slowly to avoid digestive upset.

Pellets should be fed in limited quantities - about 1/4 cup per 6 pounds of body weight daily. Choose timothy-based pellets without added seeds or colored pieces. Fresh, clean water must always be available.

## Health and Wellness

Find a rabbit-savvy veterinarian before you need one. Rabbits should be spayed or neutered for health and behavioral benefits. Annual check-ups help catch health problems early.

Watch for signs of illness: not eating, lethargy, discharge from eyes or nose, or changes in droppings. GI stasis, where the digestive system slows or stops, is a common emergency requiring immediate veterinary care.

Rabbits need their nails trimmed every 4-6 weeks. Their teeth grow continuously and should be checked regularly. Providing unlimited hay and appropriate chew toys helps keep teeth worn properly.

## Behavior and Enrichment

Rabbits are most active at dawn and dusk. They need several hours of exercise outside their enclosure daily. A rabbit-proofed area allows safe exploration - cover wires, remove toxic plants, and block access to furniture undersides.

Rabbits are intelligent and enjoy mental stimulation. Provide toys like untreated wood blocks, paper bags, and cardboard tubes. Food puzzles encourage natural foraging behavior.

Social animals, rabbits often enjoy companionship of another rabbit. Bonding rabbits requires patience and proper introduction. All rabbits in a pair or group should be spayed/neutered to prevent breeding and reduce territorial behavior.

## Understanding Rabbit Communication

Binkying - jumping and twisting in the air - indicates extreme happiness. Tooth purring (gentle teeth grinding) shows contentment. Thumping warns of perceived danger.

A relaxed rabbit lies flat with back legs extended behind (the "dead bunny flop"). Chinning objects marks them as the rabbit's territory. Grooming you shows trust and affection.

Signs of fear or aggression include growling, boxing with front paws, and showing teeth. Learn to read your rabbit's body language to understand their needs and emotions.
""",
    """# The World of Hummingbirds

Hummingbirds are tiny jewels of the bird world, captivating watchers with their iridescent colors and incredible flying abilities. These remarkable birds are found only in the Americas and bring magic to any garden.

## Amazing Abilities

Hummingbirds are the only birds that can truly hover and fly backwards. Their wings beat 50-80 times per second in normal flight and up to 200 times per second during courtship dives. This rapid movement creates the humming sound that gives them their name.

Despite weighing only 2-20 grams (about as much as a penny to a few grapes), hummingbirds have extraordinary metabolisms. Their hearts beat 500-1,200 times per minute, and they take 250 breaths per minute. They must eat every 10-15 minutes to survive.

To conserve energy at night, hummingbirds enter a state called torpor, slowing their metabolism dramatically. Their body temperature can drop from 105°F to as low as 65°F. In the morning, it takes about 20 minutes for them to "wake up" and warm up.

## Species Diversity

Over 330 species of hummingbirds exist, ranging from the 5-centimeter Bee Hummingbird (the world's smallest bird) to the 23-centimeter Giant Hummingbird. North America has about 15 breeding species, with the Ruby-throated Hummingbird most common in the east.

The Rufous Hummingbird makes the longest migration of any hummingbird - up to 3,000 miles from Alaska to Mexico. Anna's Hummingbirds are year-round residents along the Pacific coast. Many species display stunning iridescent throat patches called gorgets.

Male hummingbirds are typically more colorful than females, using their brilliant plumage to attract mates. Females are often more camouflaged to protect them while nesting. Many species show different colors depending on the angle of light.

## Creating a Hummingbird Garden

Hummingbirds are attracted to tubular flowers, especially red and orange ones. Excellent plants include bee balm, cardinal flower, trumpet vine, salvia, and fuchsia. Native plants are best as they've co-evolved with local hummingbird species.

Plan for continuous blooming from early spring through fall. Include different flower heights and shapes. Hummingbirds also eat small insects and spiders for protein, so avoid pesticides in your garden.

Provide a water source - hummingbirds enjoy misting from a fountain or sprinkler. They need perches for resting, so include small twigs and branches. Leave some spider webs intact as hummingbirds use them for nesting material.

## Hummingbird Feeders

Supplement natural food with sugar water feeders. The correct ratio is 4 parts water to 1 part white sugar - never use honey, artificial sweeteners, or red dye. Boil the water to remove chlorine and dissolve sugar, then cool before filling feeders.

Clean feeders thoroughly every 3-5 days, more often in hot weather. Mold and fermented nectar can harm hummingbirds. Use a bottle brush and rinse well - no soap residue should remain.

Place feeders where you can easily see them but also near cover for the birds. Multiple feeders placed out of sight of each other reduce territorial fighting. Bring feeders in at night in bear country.

## Nesting and Lifecycle

Hummingbird nests are tiny cups made of plant down, spider webs, and lichens. They're about the size of a walnut and stretch as the chicks grow. Females build the nest and raise the young alone.

Clutches typically contain 2 eggs, each about the size of a jelly bean. Incubation takes 14-23 days depending on species. Chicks fledge at 18-28 days but may return to the nest to sleep for another week or two.

Young hummingbirds learn to fly and feed themselves quickly. They'll visit feeders alongside adults by midsummer. By fall, most North American species begin their southward migration, often traveling alone rather than in flocks.
""",
]

TEXT_CONTENT_SMALL = [
    # Small paragraphs for text files
    """The Art of Puppy Cuddles

There's nothing quite like holding a warm, sleepy puppy in your arms. Their soft fur, tiny heartbeat, and complete trust create moments of pure joy. Puppies seem to know instinctively how to position themselves for maximum comfort, often ending up curled into impossible positions that somehow look perfectly comfortable.

New puppy owners quickly learn that these cuddle sessions are as beneficial for humans as they are for the puppies. Studies show that petting a dog lowers blood pressure and releases oxytocin in both the human and the dog. It's a beautiful mutual exchange of love and comfort.
""",
    """Wildflower Meadows

Walking through a wildflower meadow in summer is like stepping into a painting. Purple coneflowers sway alongside yellow black-eyed Susans. Orange butterfly weed attracts monarchs while pink milkweed provides food for their caterpillars.

The buzz of bees and flutter of butterflies create a symphony of movement. Each flower has evolved its own strategy for attracting pollinators, from bright colors to sweet nectar to landing platforms perfect for tired insects.
""",
    """The Secret Life of Kittens

When kittens sleep, they often dream. You can tell by their twitching whiskers, paddling paws, and tiny squeaks. Scientists believe they're processing the day's adventures and practicing their hunting skills in dreamland.

Awake, kittens are perpetual motion machines. Everything is a toy - a dust mote, a shadow, a sibling's tail. They pounce, tumble, and zoom around in bursts of energy before suddenly collapsing for another nap.
""",
    """Morning Glory Magic

Morning glories greet each day by unfurling their trumpet-shaped blooms at dawn. By afternoon, they close again, making way for tomorrow's fresh flowers. This daily ritual has charmed gardeners for centuries.

These climbing vines can grow up to 15 feet in a single season, covering fences and trellises in heart-shaped leaves and colorful blooms. Heavenly Blue is the most popular variety, but morning glories also come in purple, pink, red, and white.
""",
    """Bunny Binky

A bunny binky is one of the most joyful sights in the animal kingdom. The rabbit suddenly leaps into the air, twists its body, and kicks its feet out before landing and zooming off. It's pure, uncontrollable happiness in motion.

Rabbits binky when they feel safe, healthy, and content. A rabbit doing binkies has everything it needs - good food, comfortable housing, and often some exciting new toy or treat. It's their way of saying life is wonderful.
""",
    """Cherry Blossom Season

When cherry trees bloom, they transform landscapes into cotton candy dreams. In Japan, the tradition of hanami celebrates this fleeting beauty. Families and friends gather under the blossoms for picnics, appreciating the reminder that beautiful things don't last forever.

The blooming period typically lasts only one to two weeks. Wind and rain can shorten it further, making each petal-scattered moment precious. The falling petals, called sakura fubuki or cherry blossom blizzard, are considered as beautiful as the blooms themselves.
""",
    """Puppy Dog Eyes

Scientists have confirmed what dog lovers always knew - dogs evolved special muscles around their eyes specifically to make those irresistible puppy dog eyes at humans. This eyebrow-raising expression triggers a nurturing response in people.

Dogs use this expression most when humans are watching them. Wolves, dogs' ancestors, rarely make this face. It developed over thousands of years of domestication, a beautiful example of how dogs and humans evolved together.
""",
    """Peony Paradise

Peonies are the divas of the flower garden, and they earn every bit of their dramatic reputation. Their enormous, ruffled blooms can reach the size of dinner plates, and their fragrance is legendary - sweet, rosy, and utterly intoxicating.

These long-lived perennials can bloom for decades once established. Some peonies in botanical gardens are over 100 years old. They're slow to establish but well worth the wait, often becoming treasured heirlooms passed down through generations.
""",
    """Goldfish Memories

Contrary to popular belief, goldfish have memories lasting months, not seconds. They can learn to navigate mazes, recognize their owners, and even push levers to get food at specific times. These beautiful fish are far more intelligent than most people realize.

Goldfish can live 10-15 years with proper care, and some have reached 40 years or more. They come in many varieties beyond the common orange, including fantails, orandas, and bubble-eyes, each with unique charm.
""",
    """Rainbows After Rain

A rainbow appears when sunlight enters water droplets and bends, separating into its component colors. Red is always on the outside of the arc, violet on the inside. Sometimes, if conditions are right, you might see a double rainbow with the colors reversed on the second arc.

Every rainbow is unique to the observer. The rainbow you see is created by different water droplets than the one your friend sees standing next to you. In a way, every rainbow is your own personal light show.
""",
    """Sleeping Puppies

Puppies sleep 18-20 hours a day, and they're not being lazy - they're growing. During sleep, their bodies release growth hormones, their brains process new experiences, and their immune systems strengthen.

The positions puppies sleep in reveal a lot about how they feel. Curled up means they're conserving warmth and protecting themselves. Sprawled out means they're completely comfortable and trust their environment.
""",
    """Succulent Love

Succulents have become beloved houseplants for good reason. Their chunky leaves store water, making them forgiving of forgetful waterers. They come in an incredible array of shapes, colors, and textures, from the perfect rosettes of echeveria to the trailing strings of pearls.

These desert plants actually prefer neglect to fussing. Overwatering is the most common cause of succulent death. A bright window, well-draining soil, and water only when completely dry are all they need to thrive.
""",
    """Duckling Adventures

Baby ducks are fluffy balls of determination. Within hours of hatching, they're ready to follow their mother, swim, and search for food. Their downy feathers are water-resistant, keeping them buoyant and warm.

Ducklings imprint on the first moving thing they see after hatching, which is usually their mother. This strong bond keeps them safe as they waddle through the world, learning everything they need to know from her example.
""",
    """Hydrangea Colors

Hydrangeas are like mood rings for your garden. The same plant can produce blue or pink flowers depending on soil pH. Acidic soil creates blue blooms, while alkaline soil produces pink. White hydrangeas remain white regardless of soil conditions.

Gardeners can manipulate flower color by adjusting soil pH with additives. Aluminum sulfate increases acidity for bluer flowers. Lime makes soil more alkaline for pinker blooms. It's like having a customizable flower palette.
""",
    """Hamster Pouches

Hamster cheek pouches can stretch to hold up to 20% of the hamster's body weight in food. That's equivalent to a human carrying several watermelons in their cheeks! These expandable pockets extend from the cheeks back to the shoulders.

In the wild, hamsters use their pouches to transport food to their burrows. Pet hamsters retain this instinct, stuffing their cheeks with treats and then finding hidden spots to stash their treasures.
""",
    """Coral Bell Colors

Coral bells, or heucheras, are grown primarily for their stunning foliage rather than their flowers. The leaves come in an artist's palette of colors - deep purple, lime green, caramel orange, silver, and burgundy - often with contrasting veins.

These versatile perennials thrive in shade or partial sun, brightening dark corners of the garden. They're evergreen in mild climates, providing year-round interest. The tiny bell-shaped flowers on tall stalks are a bonus, attracting hummingbirds in spring.
""",
    """Ferret Fun

Ferrets are chaos incarnate in a long, fuzzy body. They bounce, they dance, they steal your socks. The "war dance" - a sideways hopping, back-arched, mouth-open display - means they're having the time of their lives.

These playful pets love tunnels, hammocks, and anything they can crawl through or hide in. They sleep up to 18 hours a day but pack incredible energy into their waking hours. A bored ferret will find something to do - usually something mischievous.
""",
]

TEXT_CONTENT_LARGE = [
    # Large paragraphs that exceed semantic chunk size
    """The Complete Guide to Raising Happy Puppies

Bringing a puppy home is one of life's greatest joys, but it also comes with significant responsibility. From the moment you pick up that warm, wiggling bundle of fur, you become responsible for its health, happiness, and development into a well-adjusted adult dog. The first few months are critical for establishing good habits, building trust, and setting the foundation for years of companionship. Puppies go through multiple developmental stages, each with its own challenges and rewards. The neonatal period lasts from birth to two weeks, when puppies are helpless and dependent on their mother for everything. The transitional period from two to four weeks sees their eyes and ears opening, introducing them to a world of new sensations. The socialization period from four to fourteen weeks is crucial - this is when puppies learn to interact with other dogs, humans, and their environment. What happens during this period shapes their adult personality more than any other time. The juvenile period from three to six months brings teething, increased independence, and testing of boundaries. Adolescence from six months to two years is like the teenage years - hormones surge, attention spans waver, and previously learned commands may seem forgotten. Throughout all these stages, consistency, patience, and positive reinforcement are your best tools. Puppies don't understand punishment - they understand rewards and consistency. Every interaction is a training opportunity, from meal times to play sessions to quiet evenings on the couch. The bond you build during puppyhood lasts a lifetime, making every chewed shoe and sleepless night worthwhile when you look into those adoring eyes that see you as the center of their universe.

The importance of proper nutrition cannot be overstated when raising a puppy. Their bodies are growing at an astonishing rate - a large breed puppy may increase its birth weight by 40 to 50 times in the first year. This growth requires precisely balanced nutrition, with the right amounts of protein for muscle development, calcium and phosphorus for bone growth, and DHA for brain and vision development. Too much or too little of any nutrient can cause lasting problems. Large breed puppies fed too many calories or too much calcium can develop orthopedic issues as adults. Small breed puppies with their fast metabolisms need frequent meals to maintain blood sugar levels. The best approach is to choose a high-quality puppy food appropriate for your dog's expected adult size, feed measured portions at regular times, and monitor body condition regularly. Puppies should have a visible waist when viewed from above and a slight tuck-up in the belly when viewed from the side. Ribs should be easily felt but not prominently visible. Treats are important for training but should comprise no more than 10 percent of daily calories. Fresh water should always be available. Many veterinarians recommend continuing puppy food until growth is complete - around one year for small breeds and up to two years for giant breeds. Switching to adult food too early can shortchange nutrition during crucial development periods.

Socialization is perhaps the most important thing you can do for your puppy during the critical period between three and fourteen weeks of age. During this window, puppies are primed to accept new experiences as normal. Experiences during this time shape how they respond to the world for the rest of their lives. A well-socialized puppy becomes a confident adult dog who takes new situations in stride. A poorly socialized puppy may become fearful, anxious, or aggressive when faced with unfamiliar people, animals, or environments. The goal of socialization is to expose your puppy to as many different experiences as possible in a positive way. This includes meeting people of different ages, genders, ethnicities, and appearances - people in hats, people with beards, children, elderly individuals, people using wheelchairs or crutches. It includes other animals - well-mannered adult dogs who can teach puppy social skills, cats, small animals if they'll be part of your household. It includes different environments - urban streets with traffic sounds, rural settings with livestock, pet stores, veterinary clinics, grooming salons. It includes different surfaces - grass, gravel, tile, metal grates, wobbly surfaces. It includes different sounds - vacuum cleaners, thunderstorms, fireworks, sirens. Every positive experience adds to your puppy's confidence bank. Never force a puppy into a scary situation - instead, let them approach new things at their own pace, rewarding bravery with treats and praise. If a puppy shows fear, calmly remove them from the situation without making a fuss, and try again later with more distance or less intensity. The investment you make in socialization pays dividends for life.

Training your puppy is not about teaching tricks or establishing dominance - it's about communication. Dogs don't speak human language, and humans don't naturally understand dog communication. Training builds a shared language of cues and responses that allows you to navigate life together. Start with simple cues - sit, down, come, stay - and build from there. Keep training sessions short, just five to ten minutes for young puppies, and end on a positive note. Use high-value treats and enthusiastic praise to mark desired behaviors. Timing is crucial - rewards must come within one to two seconds of the behavior for the dog to make the connection. Consistency is equally important - everyone in the household must use the same cues and reward the same behaviors. Potty training, often the most pressing concern for new puppy owners, requires management, consistency, and patience. Take your puppy out frequently - after waking, after eating, after playing, and every one to two hours in between. Go to the same spot each time and wait quietly until they go, then reward lavishly. Supervise your puppy indoors and confine them when you can't watch - crates are invaluable tools when used correctly. Accidents will happen - clean them up without fuss using enzymatic cleaners. Never punish accidents - it only teaches puppies to hide when they need to go. Most puppies achieve reliable potty training between four and six months, though some take longer. The keys are consistency, patience, and celebrating successes rather than punishing failures.
""",
    """Everything You Need to Know About Creating the Perfect Flower Garden

Creating a beautiful flower garden is both an art and a science, requiring knowledge of plant biology, design principles, and the specific conditions in your garden. The first step is understanding your site - how much sun does it receive, what type of soil do you have, how much rainfall can you expect, and what are your temperature extremes throughout the year. A garden that works in Seattle won't work in Phoenix, and a garden that thrives in full sun will fail in shade. Take time to observe your site through the seasons before committing to a plan. Notice where water collects after rain, where the first frost settles, where summer sun creates hot spots. These observations will guide plant selection and save you from expensive mistakes. Soil testing is invaluable - for a small fee, your local extension service can tell you your soil's pH, nutrient levels, and organic matter content. Most flowering plants prefer soil with a pH between 6.0 and 7.0, good drainage, and plenty of organic matter. If your soil is heavy clay, you'll need to amend it with compost and possibly grit to improve drainage. If it's sandy, compost will help it retain moisture and nutrients. Building good soil is the foundation of successful gardening - it's better to spend your budget on soil improvement than on plants that will struggle in poor soil.

Designing your flower garden begins with deciding on a style. Formal gardens use geometric shapes, symmetrical layouts, and a limited color palette for an elegant, structured look. Cottage gardens embrace informal abundance, mixing colors and textures in seemingly random but carefully planned profusion. Modern gardens often feature bold architectural plants, clean lines, and dramatic contrasts. Whatever style you choose, certain principles apply. Consider the view from inside your home - the garden should be beautiful from your most-used windows. Think about how you'll move through the garden - paths should be wide enough for comfortable walking and lead somewhere interesting. Plan for year-round interest by including plants that peak in different seasons. Use repetition to create unity - repeat colors, textures, or specific plants throughout the garden to tie it together. Create focal points that draw the eye - a specimen plant, a piece of sculpture, a beautiful container. Pay attention to scale - plants should be proportional to their surroundings and to each other. Don't forget foliage - flowers come and go, but leaves provide structure and interest throughout the growing season. Silver foliage cools down hot colors, dark foliage adds drama, and variegated leaves provide their own kind of brightness even when nothing is blooming.

Plant selection is where many gardeners go wrong, seduced by beautiful pictures in catalogs without considering whether a plant is appropriate for their conditions. Always read plant tags and catalog descriptions carefully. Note the mature size - that cute little shrub may grow into a monster that blocks your windows. Note light requirements - a full sun plant won't bloom in shade, and a shade plant will scorch in full sun. Note water needs - mixing plants with different water requirements leads to some being overwatered and others drought-stressed. Consider your climate zone and choose plants rated hardy in your area. Be realistic about maintenance - a garden full of demanding divas will quickly become a burden instead of a joy. That said, don't be afraid to experiment. Gardening is full of surprises, and sometimes plants thrive where they shouldn't or fail where they should succeed. Keep a garden journal to record what works and what doesn't. Learn from failures rather than being discouraged by them. Every experienced gardener has killed countless plants - it's how we learn.

The best flower gardens provide food and shelter for pollinators and other wildlife, creating little ecosystems buzzing with life. Choose plants that provide nectar and pollen for bees, butterflies, and hummingbirds. Native plants are especially valuable because they've co-evolved with native pollinators. Include host plants for butterfly caterpillars - monarchs need milkweed, swallowtails need fennel or parsley, painted ladies need hollyhocks. Provide water sources - even a shallow dish with pebbles for perching helps. Leave some areas a bit wild - a pile of leaves, a dead tree, a patch of bare ground - to provide habitat for beneficial insects. Avoid pesticides, which kill beneficial insects along with pests. Most pest problems can be managed through physical removal, attracting predatory insects, or simply tolerating some damage. A garden that supports wildlife is not only better for the environment but more interesting to observe. You'll never tire of watching bees lumber from flower to flower, butterflies unfurl their long proboscises to sip nectar, or hummingbirds hover with wings blurred into invisibility.

Maintaining your flower garden requires attention throughout the growing season, but good planning reduces the workload. Mulching beds with two to three inches of organic mulch suppresses weeds, retains moisture, and gradually improves soil as it decomposes. Watering deeply but infrequently encourages plants to develop deep root systems that can find water during dry spells - frequent shallow watering creates shallow roots dependent on constant irrigation. The best time to water is early morning, when evaporation is low and leaves have time to dry before nightfall. Deadheading spent flowers encourages many plants to produce more blooms and keeps the garden looking tidy. Pinching back leggy plants in early summer promotes bushier growth. Staking tall plants before they flop prevents broken stems and keeps the garden looking neat. Dividing perennials every few years maintains their vigor and gives you plants to share or move elsewhere. Fall cleanup is optional - many experts now recommend leaving seed heads and stems standing through winter to provide food and shelter for wildlife and winter interest in the garden. A layer of mulch over perennial crowns provides insulation against freeze-thaw cycles. Spring cleanup, before new growth emerges, removes last year's debris and gives you a fresh start. Throughout the season, take time to simply sit and enjoy your creation. The best gardeners are also the best observers, noticing what's thriving, what's struggling, and what unexpected beauty has emerged.
""",
    """Understanding the Secret World of Cats

Cats have shared our homes for thousands of years, yet they remain enigmatic creatures whose behavior often puzzles their human companions. Unlike dogs, who were domesticated to work alongside humans and have evolved to understand our communication, cats domesticated themselves when they discovered that human grain stores attracted rodents. This history of voluntary association rather than selective breeding for human purposes explains much about cat behavior today. Cats retain more of their wild nature than dogs do, and understanding this helps us appreciate their unique qualities rather than being frustrated by them. A cat is not a small dog, and expecting dog-like behavior leads to disappointment. Cats are solitary hunters who form social bonds on their own terms. They're crepuscular, most active at dawn and dusk when their prey would be moving. They sleep 12-16 hours a day not out of laziness but because hunting requires intense bursts of energy followed by recovery. They're obligate carnivores whose bodies are designed to process meat, not carbohydrates. They have incredibly sensitive senses - hearing frequencies up to 65 kHz compared to humans' 20 kHz, night vision that works in one-sixth the light humans need, and a sense of smell with 200 million scent receptors compared to our 5 million. When your cat stares at seemingly nothing, they may be hearing or smelling things completely beyond your perception.

Cat communication is subtle and complex, relying more on body language, scent, and context than vocalizations. Adult cats rarely meow to each other - meowing is a behavior they've developed specifically to communicate with humans, essentially training us to respond to their requests. The slow blink is often called a cat kiss - returning it tells your cat you feel safe and affectionate too. Tail position communicates mood: up means confident and friendly, puffed up means frightened or aggressive, tucked means anxious, and gently swishing means interested or playful. Ear position is equally telling: forward means alert and interested, sideways or back means annoyed or frightened. Kneading, that rhythmic pushing with the paws, is a holdover from kittenhood when it stimulated milk flow from the mother - adult cats do it when feeling safe and content. Head bunting and cheek rubbing deposit scent from glands on the cat's face, marking you as part of their territory and social group. Rolling over to show the belly doesn't necessarily mean the cat wants belly rubs - it can simply be a display of trust, and touching may result in a defensive grab. Learning to read these signals builds a deeper bond with your cat and helps avoid miscommunication.

Creating an enriching environment is essential for indoor cats, who are denied the mental and physical stimulation of outdoor life. Without appropriate outlets for their hunting instincts, cats may develop behavioral problems or become overweight and lethargic. Environmental enrichment starts with vertical space - cats feel safer when they can survey their territory from above. Cat trees, shelves, and window perches satisfy this need. Hiding spots are equally important; cats need places to retreat when stressed or simply wanting privacy. Interactive toys that mimic prey - feather wands, laser pointers, remote-controlled mice - engage hunting instincts. Rotate toys to prevent boredom, and always end play sessions by letting the cat catch something so they feel satisfied rather than frustrated. Puzzle feeders slow down eating and provide mental stimulation. Window perches let cats watch birds and squirrels - cat TV that never gets old. Scratching posts in various locations let cats stretch, maintain their claws, and mark territory. Catnip and silver vine provide occasional excitement for cats who respond to them. Even cardboard boxes and paper bags provide entertainment - never underestimate the appeal of a simple box. Regular interactive play sessions, at least 15-20 minutes daily, strengthen your bond with your cat while meeting their need for predatory play. A tired cat is a well-behaved cat.

Understanding cat health requires awareness of their tendency to hide illness. In the wild, showing weakness makes an animal vulnerable to predators and social rivals. Cats retain this instinct, masking pain and sickness until they're seriously ill. This makes regular veterinary check-ups crucial - annual exams for adult cats, twice yearly for seniors. At home, watch for subtle changes: eating less or more than usual, drinking more water, changes in litter box habits, reduced grooming or overgrooming, hiding more than usual, decreased playfulness, or subtle changes in behavior. Any of these can signal health problems. Common cat health issues include dental disease, which affects most cats over age three and can cause pain and systemic health problems if untreated; kidney disease, especially common in older cats; hyperthyroidism, also common in seniors; urinary tract problems, particularly in males; diabetes, especially in overweight cats; and various cancers. Keeping your cat at a healthy weight, feeding appropriate food, providing fresh water, keeping vaccinations current, and maintaining regular veterinary care give your cat the best chance at a long, healthy life. Many cats now live into their late teens or early twenties with good care. Those extra years of companionship are worth every effort.
""",
]

PDF_CONTENT = [
    # Content that will be converted to PDF
    """# Guide to British Shorthair Cats

## Overview

The British Shorthair is a beloved breed known for its round face, dense coat, and calm demeanor. These chunky, teddy bear-like cats have been capturing hearts since Roman times when they likely arrived in Britain with Roman soldiers.

## Appearance

British Shorthairs have distinctive rounded features. Their large, round eyes can be copper, gold, blue, or green depending on coat color. The "British Blue" with its gray-blue coat and copper eyes is the most iconic variety, though the breed comes in many colors and patterns.

Their dense, plush coat feels crisp to the touch, almost like velvet. It requires minimal grooming - weekly brushing is usually sufficient. These stocky cats have powerful bodies and short, strong legs.

## Personality

British Shorthairs are calm, easygoing cats who enjoy a peaceful life. They're affectionate without being demanding, often content to sit nearby rather than on your lap. They're generally quiet cats who get along well with children and other pets.

These independent cats can entertain themselves but appreciate interactive play sessions. They're not as active as some breeds but maintain a playful spirit well into adulthood.
""",
    """# The Magic of Monarch Butterflies

## Migration Marvel

Every fall, millions of monarch butterflies travel up to 3,000 miles from the United States and Canada to their wintering grounds in central Mexico. This incredible journey is one of nature's most remarkable phenomena.

## Life Cycle

Monarchs go through complete metamorphosis: egg, caterpillar, chrysalis, and adult butterfly. The distinctive black, yellow, and white striped caterpillars feed exclusively on milkweed plants, which make them toxic to predators.

## Conservation

Monarch populations have declined dramatically due to habitat loss and climate change. Planting native milkweed and avoiding pesticides helps support these beautiful butterflies. Their annual migration is now listed as endangered.
""",
    """# Beagle Breed Profile

## Friendly Hound

Beagles are cheerful, friendly dogs originally bred for hunting rabbits. Their excellent noses and compact size made them perfect for following scent trails through underbrush. Today, they make wonderful family companions.

## Appearance and Size

Beagles typically weigh 20-30 pounds and stand 13-15 inches tall. They have a short, weather-resistant coat in classic hound colors: tricolor, red and white, or lemon and white. Their large brown eyes and long, velvety ears give them an irresistibly appealing expression.

## Temperament

These merry hounds love company and don't do well left alone for long periods. They're great with children and other dogs but may chase smaller pets due to their hunting heritage. Beagles are food-motivated, making training easier but also making them prone to counter-surfing and garbage raiding.

## Exercise Needs

As scent hounds, Beagles need daily exercise and mental stimulation. They excel at nose work games and tracking activities. A secure fence is essential as they will follow an interesting scent without regard for boundaries.
""",
    """# Orchid Care for Beginners

## Introduction to Orchids

Orchids have a reputation for being difficult, but many varieties are surprisingly easy to grow. The moth orchid (Phalaenopsis) is perfect for beginners, thriving in typical home conditions and blooming for months at a time.

## Light Requirements

Most orchids prefer bright, indirect light. An east-facing window is ideal. Direct sunlight can burn leaves, while too little light prevents blooming. Yellowing leaves may indicate too much light; dark green leaves suggest insufficient light.

## Watering Wisdom

The number one killer of orchids is overwatering. Most orchids need water only when their potting medium is nearly dry. Water thoroughly, allowing excess to drain, then don't water again until the medium approaches dryness.

## Reblooming Secrets

After flowers fade, cut the spike above a node to encourage a secondary spike, or cut it at the base for stronger regrowth. Cool night temperatures (55-65°F) for several weeks often trigger reblooming. With proper care, orchids will bloom repeatedly for years.
""",
    """# Cavalier King Charles Spaniel Guide

## Royal Heritage

Named after King Charles II who adored his spaniels, Cavaliers are true companion dogs bred for centuries to be loving lap warmers. Their gentle, affectionate nature makes them ideal therapy dogs and family pets.

## Four Colors

Cavaliers come in four official colors: Blenheim (chestnut and white), tricolor (black, white, and tan), black and tan, and ruby (solid reddish-brown). All colors share the same sweet expression and silky coat.

## Adaptable Companions

These versatile dogs adapt to various lifestyles. They're happy with apartment living if exercised regularly, yet athletic enough for hiking and agility. They get along with everyone - children, other dogs, cats, and strangers alike.

## Health Awareness

Cavaliers are prone to heart disease (mitral valve disease) and neurological conditions. Choosing a reputable breeder who screens for health issues is essential. Despite these concerns, well-bred Cavaliers can live happy lives of 9-14 years.
""",
    """# Growing Sunflowers: A Complete Guide

## Why Grow Sunflowers?

Sunflowers bring instant happiness to any garden. Their cheerful faces follow the sun across the sky, and they're remarkably easy to grow. From tiny dwarf varieties to towering giants, there's a sunflower for every garden.

## Planting Tips

Plant seeds directly in the garden after the last frost, about 1 inch deep and 6 inches apart. Choose a spot with full sun and average soil - sunflowers aren't fussy. Thin seedlings to 12-24 inches apart depending on variety.

## Growing Care

Water deeply but infrequently once established. Tall varieties may need staking in windy areas. Sunflowers are relatively pest-free, though birds and squirrels will compete for the seeds. Some gardeners cover developing heads with mesh to protect the harvest.

## Harvesting Seeds

For eating, harvest when the back of the head turns brown and seeds look plump. Cut the head with a foot of stem attached, hang in a dry place, and rub out seeds when fully dry. One sunflower head can produce hundreds of delicious seeds.
""",
    """# The Ragdoll Cat: A Gentle Giant

## Origin Story

Ragdolls were developed in California in the 1960s from a white Persian-type cat named Josephine. The breed is named for their tendency to go limp and relaxed when picked up, like a child's ragdoll toy.

## Striking Appearance

These large cats (15-20 pounds for males) have semi-long, silky coats in pointed patterns: seal, blue, chocolate, lilac, red, and cream. Their striking blue eyes and sweet expression are irresistible. Despite their long fur, they lack an undercoat and mat less than many long-haired breeds.

## Personality Plus

Ragdolls are often called "dog-like" for their tendency to follow their owners around, greet them at the door, and play fetch. They're gentle, patient, and usually good with children and other pets. They're not typically jumpers and prefer to stay at ground level.

## Indoor Cats

Ragdolls' trusting nature makes them vulnerable outdoors. They lack the wariness and fighting ability of more street-smart cats. They're best kept as indoor cats with plenty of enrichment and human interaction.
""",
    """# Daffodil Growing Guide

## Harbingers of Spring

Daffodils are among the first flowers to bloom in spring, their cheerful yellow and white trumpets announcing winter's end. These reliable bulbs naturalize readily, returning year after year with increasing numbers of blooms.

## Planting Basics

Plant bulbs in fall, about 6 inches deep and 3-6 inches apart, with the pointed end up. Choose a location with full sun to partial shade and well-drained soil. Daffodils are deer and rodent resistant, making them ideal for gardens with wildlife pressure.

## Division and Care

Every few years, when flowering decreases, dig and divide crowded clumps after foliage dies back. Let foliage yellow naturally after blooming - it's feeding next year's flowers. Deadhead spent blooms but leave stems to photosynthesize.

## Forcing Indoors

Bring spring indoors by forcing daffodils in pots. Pot bulbs in fall, chill for 12-15 weeks in a cold (35-45°F) dark location, then bring into warmth and light. They'll bloom in 3-4 weeks, bringing sunshine to winter windowsills.
""",
    """# Norwegian Forest Cat: Viking Companion

## Ancient Origins

Norwegian Forest Cats, called "Skogkatt" in Norway, are ancient cats mentioned in Norse mythology. They likely traveled with Vikings on their ships, controlling rodent populations. Their thick coats evolved to survive harsh Scandinavian winters.

## Impressive Appearance

These large cats (12-16 pounds) have semi-long, water-resistant coats with a dense undercoat. Their almond-shaped eyes, triangular heads, and tufted ears give them a wild appearance. A magnificent ruff around the neck adds to their majestic look.

## Personality Traits

Despite their wild appearance, Norwegian Forest Cats are gentle and friendly. They're moderately active, enjoying climbing and playing but also happy to relax. They're generally good with children and other pets, though they bond most closely with their own family.

## Grooming Needs

Their thick coats need regular grooming, especially during spring and fall shedding. Weekly brushing usually suffices, increasing to daily during heavy shedding. Their water-resistant outer coat resists matting better than many long-haired breeds.
""",
    """# Pomeranian Personality

## Tiny Dog, Big Character

Pomeranians pack enormous personality into tiny bodies. These spirited little dogs descend from large sled dogs and retain their ancestors' bold, curious nature despite weighing only 3-7 pounds.

## Foxy Features

Pomeranians have distinctive foxy faces with alert expressions and bright, intelligent eyes. Their luxurious double coat forms a frill around the chest and a plumed tail that fans over the back. They come in nearly every color and pattern imaginable.

## Temperament

These confident little dogs are lively and playful, enjoying both active play and lap time. They're intelligent and trainable but can be stubborn. Early socialization is important as they can be suspicious of strangers and feisty with other dogs regardless of size difference.

## Care Considerations

Pomeranians need regular grooming to maintain their fluffy coats. They're prone to dental problems, so tooth brushing is important. Their small size makes them fragile - they're not ideal for homes with young children who might accidentally injure them.
""",
    """# Creating a Pollinator Garden

## Why Pollinators Matter

Pollinators - bees, butterflies, hummingbirds, and others - are essential for reproducing many food crops and wildflowers. Their populations are declining due to habitat loss and pesticide use. A pollinator garden helps by providing food and shelter.

## Plant Selection

Choose native plants when possible, as they've co-evolved with local pollinators. Include flowers with different shapes to serve different pollinators: tubular flowers for hummingbirds, flat landing pads for butterflies, and small clustered flowers for bees.

## Design Tips

Plant in groups - pollinators find larger patches of flowers more easily than scattered single plants. Plan for continuous bloom from early spring through late fall. Include larval host plants for butterflies. Leave some bare ground for ground-nesting bees.

## Maintenance

Avoid pesticides, which harm pollinators along with pests. Leave some fallen leaves and dead stems for overwintering insects. Provide a shallow water source with pebbles for perching. Your garden will reward you with increased wildlife activity and better fruit and vegetable yields.
""",
    """# Scottish Fold Cats

## Unique Ears

Scottish Folds are instantly recognizable by their folded ears, caused by a cartilage defect that makes the ears bend forward and down. Not all Scottish Folds have folded ears - some have straight ears (Scottish Straights) due to genetics.

## Round and Sweet

Beyond their signature ears, Scottish Folds have round faces, round bodies, and round eyes giving them an owl-like appearance. They're medium-sized cats with dense, plush coats in many colors. Their expressions are often described as sweet or surprised.

## Gentle Companions

Scottish Folds are known for their sweet, calm personalities. They're not overly demanding of attention but enjoy being near their people. They're generally quiet cats who get along well with children and other pets. Many Scottish Folds sit in the distinctive "Buddha position" with their legs stretched out.

## Health Considerations

The gene causing folded ears also affects cartilage throughout the body and can cause painful joint problems. Ethical breeding pairs fold-eared cats with straight-eared cats to minimize issues. Always buy from breeders who screen for joint problems.
""",
    """# Caring for Koi Fish

## Living Jewels

Koi are ornamental varieties of the common carp, bred for their beautiful colors and patterns. These long-lived fish can survive 25-35 years with proper care, with some individuals living over 100 years.

## Pond Requirements

Koi need large ponds - at least 1,000 gallons for a small collection. Water depth should be at least 3 feet to protect fish from temperature extremes and predators. Filtration is essential as koi produce significant waste. Include areas of shade and shelter.

## Feeding

Koi are omnivores who eat both plant matter and small invertebrates. Feed high-quality koi pellets as a staple, with occasional treats of watermelon, peas, or shrimp. Feed only what they can consume in 5 minutes. Reduce feeding in cold weather when metabolism slows.

## Variety and Color

Koi come in dozens of recognized varieties based on color and pattern. Kohaku (white with red) is considered the king of koi. Other popular varieties include Sanke (white, red, and black) and Showa (black with red and white). Colors can change with age, diet, and water quality.
""",
    """# Border Collie Intelligence

## Smartest Breed

Border Collies consistently rank as the most intelligent dog breed. Originally bred for herding sheep in the border region between England and Scotland, they possess an intense focus, problem-solving ability, and eagerness to work that sets them apart.

## Physical Attributes

Medium-sized dogs (30-55 pounds), Border Collies have athletic builds designed for endurance. Their coats can be rough or smooth, in black and white, tricolor, red, or merle patterns. Their intense, watchful eyes - often brown but sometimes blue - reflect their alert minds.

## Herding Instincts

Border Collies use "the eye" - an intense stare - to control livestock. This same focus extends to everything they do. Without appropriate outlets, they may try to herd children, other pets, or even cars. They need mental challenges as much as physical exercise.

## Lifestyle Requirements

Border Collies are not for casual pet owners. They need hours of exercise and mental stimulation daily. They excel in agility, obedience, herding trials, and nose work. A bored Border Collie becomes destructive and neurotic. With the right owner who can keep them busy, they're extraordinary companions.
""",
    """# Wisteria: Cascading Beauty

## Dramatic Display

Few sights match the beauty of wisteria in full bloom. Cascading clusters of fragrant purple, pink, or white flowers drape from pergolas and arbors, creating romantic scenes in spring. These vigorous vines can live for over 100 years.

## Types of Wisteria

Japanese wisteria (Wisteria floribunda) has the longest flower clusters, up to 3 feet. Chinese wisteria (Wisteria sinensis) blooms more reliably but can be invasive. American wisteria (Wisteria frutescens) is smaller and better behaved.

## Growing Requirements

Wisteria needs strong support - mature vines can pull down weak structures. Plant in full sun with average soil. Established wisterias are drought-tolerant. Prune twice yearly: in summer to control growth, and in late winter to encourage bloom.

## Patience Required

Wisteria can take 7-15 years to bloom from seed, though cutting-grown plants bloom sooner. To encourage blooming on reluctant plants, try root pruning, reducing nitrogen, or providing cooler winter temperatures. The wait is worth it when those glorious blooms finally appear.
""",
    """# Russian Blue: Elegant Mystery

## Distinctive Appearance

Russian Blues are elegant cats with silver-blue coats that shimmer in the light. Their bright green eyes stand out against their grey faces. Their dense double coats are incredibly soft and stand out from the body, giving them a plush appearance.

## Quiet Companions

These reserved cats take time to warm up to strangers but are devoted to their families. They're quiet, gentle, and sensitive to their owners' moods. Russian Blues often follow their favorite person from room to room, supervising their activities.

## Playful Side

Despite their dignified appearance, Russian Blues have a playful streak. They enjoy interactive toys and games, and can learn tricks. They're known for their love of fetch and their enjoyment of climbing to high places to survey their domain.

## Easy Care

Russian Blues are relatively low-maintenance cats. Their short, dense coats need only weekly brushing. They're generally healthy cats with no breed-specific health issues. They're fastidious about their litter boxes and prefer them spotlessly clean.
""",
]


def ensure_dirs():
    os.makedirs(LOCAL_DIR, exist_ok=True)
    os.makedirs(GITHUB_DIR, exist_ok=True)


def write_md_file(path, content):
    with open(path, "w") as f:
        f.write(content)


def write_txt_file(path, content):
    with open(path, "w") as f:
        f.write(content)


def write_pdf_file(path, content):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        temp_md = f.name

    try:
        subprocess.run(
            [
                "pandoc",
                temp_md,
                "-o",
                path,
                "--pdf-engine=pdflatex",
                "-V",
                "geometry:margin=1in",
            ],
            check=True,
            capture_output=True,
        )
    finally:
        os.unlink(temp_md)


def generate_local_files():
    """Generate 50 files in the local directory."""
    print("Generating local files...")
    file_count = 0

    # Keep existing file
    # best-cats.md already exists

    # Small markdown files (13 files to reach ~17 total with existing)
    small_md_names = [
        "persian-cat-care.md",
        "golden-retriever-puppies.md",
        "sunflower-tips.md",
        "holland-lop-bunnies.md",
        "butterfly-garden.md",
        "hamster-happiness.md",
        "kitten-playtime.md",
        "tulip-varieties.md",
    ]
    for i, name in enumerate(small_md_names):
        write_md_file(f"{LOCAL_DIR}/{name}", SMALL_MD_CONTENT[i])
        file_count += 1

    # Large markdown files (8 files)
    large_md_names = [
        "maine-coon-complete-guide.md",
        "labrador-retriever-guide.md",
        "cottage-garden-creation.md",
        "rabbit-care-complete.md",
    ]
    for i, name in enumerate(large_md_names):
        write_md_file(f"{LOCAL_DIR}/{name}", LARGE_MD_CONTENT[i])
        file_count += 1

    # Text files - small (13 files)
    small_txt_names = [
        "puppy-cuddles.txt",
        "wildflower-meadows.txt",
        "secret-life-kittens.txt",
        "morning-glory-magic.txt",
        "bunny-binky.txt",
        "cherry-blossoms.txt",
        "puppy-dog-eyes.txt",
        "peony-paradise.txt",
        "goldfish-memories.txt",
        "rainbows.txt",
        "sleeping-puppies.txt",
        "succulent-love.txt",
        "duckling-adventures.txt",
    ]
    for i, name in enumerate(small_txt_names):
        write_txt_file(f"{LOCAL_DIR}/{name}", TEXT_CONTENT_SMALL[i])
        file_count += 1

    # Text files - large (4 files)
    large_txt_names = [
        "raising-happy-puppies.txt",
        "perfect-flower-garden.txt",
        "understanding-cats.txt",
    ]
    for i, name in enumerate(large_txt_names):
        write_txt_file(f"{LOCAL_DIR}/{name}", TEXT_CONTENT_LARGE[i])
        file_count += 1

    # PDF files (16 files)
    pdf_names = [
        "british-shorthair-guide.pdf",
        "monarch-butterflies.pdf",
        "beagle-profile.pdf",
        "orchid-care.pdf",
        "cavalier-spaniel-guide.pdf",
        "growing-sunflowers.pdf",
        "ragdoll-cat-guide.pdf",
        "daffodil-growing.pdf",
        "norwegian-forest-cat.pdf",
        "pomeranian-guide.pdf",
        "pollinator-garden.pdf",
        "scottish-fold-cats.pdf",
        "koi-fish-care.pdf",
        "border-collie-intelligence.pdf",
        "wisteria-guide.pdf",
        "russian-blue-cats.pdf",
    ]
    for i, name in enumerate(pdf_names):
        print(f"  Creating PDF: {name}")
        write_pdf_file(f"{LOCAL_DIR}/{name}", PDF_CONTENT[i])
        file_count += 1

    print(f"Created {file_count} files in {LOCAL_DIR} (plus 1 existing)")


def generate_github_files():
    """Generate 50 files in the github directory."""
    print("Generating github files...")
    file_count = 0

    # Keep existing file
    # cats-i-hate.md already exists

    # Small markdown files (use remaining small content)
    small_md_names = [
        "guinea-pig-sounds.md",
        "lavender-benefits.md",
        "cockatiel-personality.md",
        "daisy-chains.md",
        "pygmy-goats.md",
        "rose-garden-care.md",
        "hedgehog-habits.md",
        "pansy-colors.md",
        "chinchilla-dust-baths.md",
    ]
    for i, name in enumerate(small_md_names):
        write_md_file(f"{GITHUB_DIR}/{name}", SMALL_MD_CONTENT[i + 8])
        file_count += 1

    # Large markdown files
    large_md_names = [
        "hummingbird-world.md",
        "maine-coon-guide-extended.md",
        "labrador-complete.md",
        "cottage-garden-design.md",
        "rabbit-owner-guide.md",
    ]
    large_md_content_2 = [
        LARGE_MD_CONTENT[4],
        LARGE_MD_CONTENT[0],
        LARGE_MD_CONTENT[1],
        LARGE_MD_CONTENT[2],
        LARGE_MD_CONTENT[3],
    ]
    for i, name in enumerate(large_md_names):
        write_md_file(f"{GITHUB_DIR}/{name}", large_md_content_2[i])
        file_count += 1

    # Text files - small (use remaining small content)
    small_txt_names = [
        "hydrangea-colors.txt",
        "hamster-pouches.txt",
        "coral-bells.txt",
        "ferret-fun.txt",
        "puppy-joy.txt",
        "wildflower-walks.txt",
        "kitten-dreams.txt",
        "morning-glories.txt",
        "bunny-happiness.txt",
        "cherry-blossom-magic.txt",
        "puppy-expressions.txt",
        "peony-perfection.txt",
        "goldfish-facts.txt",
        "rainbow-science.txt",
    ]
    for i, name in enumerate(small_txt_names):
        content_idx = (i + 13) % len(TEXT_CONTENT_SMALL)
        write_txt_file(f"{GITHUB_DIR}/{name}", TEXT_CONTENT_SMALL[content_idx])
        file_count += 1

    # Text files - large
    large_txt_names = [
        "complete-puppy-guide.txt",
        "flower-gardening-secrets.txt",
        "cat-behavior-explained.txt",
    ]
    for i, name in enumerate(large_txt_names):
        write_txt_file(f"{GITHUB_DIR}/{name}", TEXT_CONTENT_LARGE[i])
        file_count += 1

    # PDF files
    pdf_names = [
        "siamese-cats.pdf",
        "butterfly-migration.pdf",
        "golden-retriever-profile.pdf",
        "succulent-care.pdf",
        "labrador-profile.pdf",
        "dahlia-growing.pdf",
        "birman-cats.pdf",
        "tulip-guide.pdf",
        "siberian-cats.pdf",
        "corgi-guide.pdf",
        "bee-garden.pdf",
        "bengal-cats.pdf",
        "pond-fish.pdf",
        "australian-shepherd.pdf",
        "rose-care.pdf",
        "abyssinian-cats.pdf",
    ]
    for i, name in enumerate(pdf_names):
        print(f"  Creating PDF: {name}")
        write_pdf_file(f"{GITHUB_DIR}/{name}", PDF_CONTENT[i % len(PDF_CONTENT)])
        file_count += 1

    print(f"Created {file_count} files in {GITHUB_DIR} (plus 1 existing)")


if __name__ == "__main__":
    ensure_dirs()
    generate_local_files()
    generate_github_files()
    print("\nDone! Sample data generated successfully.")
