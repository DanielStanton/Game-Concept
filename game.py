import random, math, pygame
BACKGROUND = (0, 0, 0)

def findDistance(point1, point2):
    '''
    Finds the distance between two points
    '''
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt(((x2 - x1) ** 2) + ((y2 - y1) ** 2))

def normalizeVector(vector):
    '''
    Normalizes a two-dimensional vector, given in tuple format, and
    returns the normalized x and y components in tuple form.
    '''

    # Store the x and y components
    x = vector[0]
    y = vector[1]

    # Calculate the magnitude of the vector formed by the x and y components
    u = math.sqrt((x**2) + (y**2))

    # Normalize each component
    newX = (x / u)
    newY = (y / u)
    return(newX, newY)

def checkColourInSurface(surface, colour):
    '''
    Checks if a given colour is within a given surface and returns
    True or False accordingly.
    '''
    # Store the size of the surface
    size = surface.get_size()

    # Declare a variable to store whether or not the colour is found
    colourInSurface = False

    # Loop through each pixel in the surface
    for i in range(size[0]):
        for j in range(size[1]):

            # If the colour is found, set the boolean to True and break the loop
            if surface.get_at((i, j)) == colour:
                colourInSurface = True
                break
        if colourInSurface:
            break
    return colourInSurface
    

class Character():
    '''
    A class that represents a character in the game. The character speed,
    damage, and HP values, a pygame Surface (whose size is based on its
    HP), as well the colour and position of that Surface. The Character can
    take steps up to its speed towards a point, be wounded (which appears as
    "holes" in the Surface), or attack.
    '''

    # Speed, damage and hp are given as percentages, so they have multipliers
    # to give the actual values from the given perspectives
    BASE_SPEED = 1
    BASE_DAMAGE = 1
    BASE_HP = 10

    # Size is based on hp, so the multiplier controls the ratio of hp
    # to pixels
    BASE_SIZE = 0.1

    # Stores the speed of bullets
    BULLET_SPEED = 1
    DEATH_DISTANCE = 10000

    # List of instances of Character
    characters = []

    def __init__(self, name, speed, damage, hp, colour, position, melee, lifetime=-1):

        # Store the attributes of the Character
        self.name = name
        self.speed = math.ceil(speed * Character.BASE_SPEED)
        self.damage = math.ceil(damage * Character.BASE_DAMAGE)
        self.hp = hp * Character.BASE_HP
        self.currHP = self.hp
        self.colour = colour
        self.position = position
        self.melee = melee
        self.lifetime = lifetime
        self.currLife = 0

        # Calculate the size of the Character's surface then create it
        self.size = math.ceil(Character.BASE_SIZE * self.hp)
        self.surface = pygame.Surface((self.size, self.size))
        self.surface.fill(colour)

        # Set the state of the Character to not attacking
        self.isAttacking = False

        # If the Character is ranged, store its midpoints, which are used to
        # determine where the bullets are launched from

        # List of Character's bullets and set of their numbers is created
        # regardless of whether or not the Character is melee because
        # bullets are used on death of all Characters
        self.bullets = []
        self.bulletNumsUsed = set()

        # Store the midpoints of the character to store where the bullet
        # will shoot from
        self.midpoints = [
                (math.ceil(self.size / 2), 0),
                (self.size, math.ceil(self.size / 2)),
                (math.ceil(self.size / 2), self.size),
                (0, math.ceil(self.size / 2))
                ]
        for i in range(len(self.midpoints)):
            self.midpoints[i] = (self.midpoints[i][0] + self.position[0],
                                 self.midpoints[i][1] + self.position[1])
                
        # Add the character to the list of Characters
        Character.characters.append(self)

    def __str__(self):
        '''
        Returns the string representation of the Character
        '''
        return """Name: %s
Speed: %s
Damage: %s
MaxHP: %s
CurrentHP: %s
Size: %s
               """ % (self.name, self.speed, self.damage, self.hp,
                      self.currHP, self.size)

    # Getters and setters of the elements of the character
    # Certain elements do not have setters, or their setters are private
    # Increment functions increase elements by their base unit
    def getName(self):
        return self.name

    def getSpeed(self):
        return self.speed
    def setSpeed(self, speed):
        self.speed = math.ceil(speed * Character.BASE_SPEED)
    def incrementSpeed(self):
        self.speed = math.ceil(self.speed + Character.BASE_SPEED)

    def getDamage(self):
        return self.damage
    def setDamage(self, damage):
        self.damage = math.ceil(damage * Character.BASE_DAMAGE)
    def incrementDamage(self):
        self.damage = math.ceil(self.damage + Character.BASE_DAMAGE)

    def getSurface(self):
        return self.surface
    def _setSurface(self, size):
        self.surface = pygame.transform.scale(self.surface, (size, size))
    def render(self, surface):
        '''
        Draws the Character on a surface.
        '''
        surface.blit(self.surface, self.position)
        '''
        for bulletTuple in self.bullets:
            bullet = bulletTuple[0]
            bulletVelocity = bulletTuple[1]
            bullet.step(bulletVelocity)
            bullet.render(surface)
            '''

    # If the size is changed, the Surface must be changed
    def getSize(self):
        return self.size
    def _setSize(self):
        self.size = math.ceil(Character.BASE_SIZE * self.hp)
        self._setSurface(self.size)
    def _incrementSize(self):
        self.size = math.ceil(self.size + Character.BASE_SIZE)
        self._setSurface(self.size)

    # If the maximum HP is changed, the size must also change
    def getHP(self):
        return self.hp
    def setHP(self, hp):
        self.hp = math.ceil(hp * Character.BASE_HP)
        self._setSize()
    def incrementHP(self):
        self.hp = math.ceil(self.hp + Character.BASE_HP)
        self._incrementSize()

    def getCurrHP(self):
        return self.currHP
    def setCurrHP(self, hp):
        newHP = math.ceil(hp * Character.BASE_HP)
        if newHP > self.hp:
            self.currHP = self.hp
        else:
            self.currHP = newHP
    def incrementCurrHP(self):
        newHP = math.ceil(self.currHP + Character.BASE_HP)
        if newHP > self.hp:
            self.currHP = self.hp
        else:
            self.currHP = newHP

    def getColour(self):
        return self.colour
    def setColour(self, colour):
        newSurface = pygame.Surface((self.size, self.size))
        pygame.transform.threshold(newSurface, self.surface, BACKGROUND,
                                   (0, 0, 0, 0), (colour[0], colour[1],
                                                  colour[2], 255))
        self.surface = newSurface
        self.colour = colour

    def getPosition(self):
        return self.position
    def setPosition(self, position):
        self.position = position
        if not self.melee:
            for i in range(len(self.midpoints)):
                    self.midpoints[i] = (self.midpoints[i][0] + self.position[0],
                                         self.midpoints[i][1] + self.position[1])
    def step(self, directionVector):
        '''
        Moves the Character one step (a change in position equal to the
        Character's speed) along a given vector.
        '''

        # Normalize the given vector to produce the x and y components
        # of its unit vector
        step = normalizeVector(directionVector)

        # Multiply the components by the Character's speed, and update the
        # Character's position
        xStep = step[0] * self.speed
        yStep = step[1] * self.speed
        self.setPosition((self.position[0] + xStep,
                         self.position[1] + yStep))
    def stepDestination(self, destination):
        '''
        Moves the Character one step (a change in position equal to the
        Character's speed) towards a given point
        '''
        
        deltaX = destination[0] - self.position[0]
        deltaY = destination[1] - self.position[1]
        self.step((deltaX, deltaY))

    def wound(self, damage):
        '''
        Deals a given amount of damage to the Character. A surface is created
        to be drawn on the Character surface to represent a wound. The size
        of the wound is proportional to how much damage is dealt. So dealing
        damage equal to half the HP of the Character creates a wound
        approximately half the size of the Character surface. After drawing
        the wound, the current hp is updated.
        '''

        # Store the factor needed to make the ratio of wound size to
        # Character size approximately equal to the ratio of damage to hp
        weirdNumber = math.sqrt(self.hp / damage)

        # Calculate the wound size
        woundSize = math.ceil(damage * Character.BASE_SIZE * weirdNumber)

        # If the wound size is less than the Character size, the Character
        # wasn't completely destroyed, so place the wound
        if woundSize < self.size:

            # Randomly select a location for the wound. If the location is
            # already a wound, continue generating new locations until
            # the check limit is reached
            isBackground = True
            checkCount = 0
            checkLimit = self.size
            while isBackground:
                woundX = random.randint(0, self.size - woundSize)
                woundY = random.randint(0, self.size - woundSize)

                # Check the area taken up by the wound to see if it is
                # an already wounded area
                checkSurface = self.surface.subsurface(pygame.Rect(woundX,
                                                                   woundY,
                                                                   woundSize,
                                                                   woundSize))
                isBackground = checkColourInSurface(checkSurface, BACKGROUND)

                # If the area taken up by the wound is already a wounded
                # area, allow that location to be used after the check
                # limit is reached
                if isBackground:
                    checkCount += 1
                    if checkCount > checkLimit:
                        isBackground = False
            
            # Draw the wound on the Character
            woundSurface = pygame.Surface((woundSize, woundSize))
            woundSurface.fill(BACKGROUND)
            self.surface.blit(woundSurface, (woundX, woundY))
        else:
            self.currHP = 0

        if damage > self.currHP:
            self.currHP = 0
        else:
            self.currHP -= damage

    def getMelee(self):
        return self.melee
    def setMelee(self, melee):
        self.melee = melee
    def toggleMelee(self):
        self.melee = not self.melee

    def getIsAttacking(self):
        return self.isAttacking
    def setIsAttacking(self, isAttacking):
        self.isAttacking = isAttacking

    def setLifetime(self, lifetime):
        self.lifetime = lifetime

    def attack(self, target, isDeath=False):
        if self.melee:
            #step towards point
            p=5

        if not self.melee or isDeath:
            # Get the num of the next bullet. If that number is already used,
            # find another one
            bulletNum = len(self.bullets)
            if bulletNum in self.bulletNumsUsed:
                for i in range(1, len(self.bullets) + 1):
                    if i not in self.bulletNumsUsed:
                        bulletNum = i
                        break
            self.bulletNumsUsed.add(bulletNum)

            # Calculate the damage, hp, colour, and size of the bullet
            bulletDamage = self.damage / Character.BASE_DAMAGE
            bulletHP = bulletDamage
            bulletColour = self.colour
            bulletSize = math.ceil(bulletHP * Character.BASE_HP * Character.BASE_SIZE)

            # Calculate where the bullet starts based on which side of the
            # Character is closest to the target
            closestPoint = ()
            bulletPosition = ()
            for i in range(len(self.midpoints)):
                if i == 0:
                    closestPoint = self.midpoints[i]
                    bulletPosition = (self.midpoints[i][0] - math.ceil(bulletSize / 2),
                                      self.midpoints[i][1] - bulletSize)
                elif findDistance(self.midpoints[i], target) < findDistance(closestPoint,
                                                                            target):
                    closestPoint = self.midpoints[i]
                    if i == 1:
                        bulletPosition = (self.midpoints[i][0],
                                          self.midpoints[i][1] - math.ceil(bulletSize / 2))
                    elif i == 2:
                        bulletPosition = (self.midpoints[i][0] - math.ceil(bulletSize / 2),
                                          self.midpoints[i][1])
                    elif i == 3:
                        bulletPosition = (self.midpoints[i][0] - bulletSize,
                                          self.midpoints[i][1] - math.ceil(bulletSize / 2))

            # Create the bullet as a Character
            bullet = Character((self.name + "Bullet" + str(bulletNum)),
                                Character.BULLET_SPEED, bulletDamage, bulletHP,
                                bulletColour, bulletPosition, True)

            # If the bullets are being released upon Death, they only
            # travel a certain distance before disappearing
            if isDeath:
                Character.characters.remove(bullet)
                lifetime = math.ceil(Character.DEATH_DISTANCE / Character.BULLET_SPEED)
                bullet = Character((self.name + "Bullet" + str(bulletNum)),
                                Character.BULLET_SPEED, bulletDamage, bulletHP,
                                bulletColour, bulletPosition, True, lifetime)

            # Calculate the velocity of the bullet
            bulletDistance = (target[0] - bulletPosition[0],
                              target[1] - bulletPosition[1])
            bulletVelocity = normalizeVector(bulletDistance)

            # Set the bullet's isAttacking to True and add the bullet to the
            # Character's list of bullets
            bullet.setIsAttacking(True)
            self.bullets.append((bullet, bulletVelocity))

            # If the bullets are bullets released upon death, they should
            # not cause damage to other Characters
            if isDeath:
                bullet.setIsAttacking(False)

    def update(self):
        self.currLife += 1
        for bulletTuple in self.bullets:
            bullet = bulletTuple[0]
            bulletVelocity = bulletTuple[1]
            bullet.step(bulletVelocity)
            bullet.render(surface)
            bullet.update()
        # check collisions
        if self.currHP == 0:
            self._die()
        if self.currLife == self.lifetime:
            self.surface.fill(BACKGROUND)
        

    def _explode(self):
        numPieces = random.randint(4, 12)
        for i in range(numPieces):
            explodeLocation = (random.randint(self.position[0] - 5,
                                              self.position[0] + self.size + 5),
                               random.randint(self.position[1] - 5,
                                              self.position[1] + self.size + 5))
            self.attack(explodeLocation, True)

    def _die(self):
        self.surface.fill(BACKGROUND)
        self._explode()
        Character.characters.remove(self)

pygame.init()
x = pygame.display.set_mode((1000, 800))
  

a = Character("Jeremy", 5, 5, random.randint(10, 100), (255, 0, 0),
              (random.randint(50, 300), random.randint(50, 300)), True)
print(a)
while True:
    x.fill(BACKGROUND)
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            '''
            target = (random.randint(50, 300), random.randint(50, 300))
            a.attack(target)
            '''
            y = random.randint(1, 100) * Character.BASE_DAMAGE
            a.wound(y)
            print(y)
            print(a)
            a.update()
            
            
    for character in Character.characters:
        character.update()
        character.render(x)
    pygame.display.update()

        
