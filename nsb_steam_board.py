import datetime

import nsb_database
import nsb_format_points
import nsb_steam
##character
#All-Char, story mode, Aria, Bard, Bolt, Cadence, Coda, Dorian, Dove, Eli,  Melody, Monk, None

##Mode
#Speed, Score,  Deathless, Daily, None

##dlc
#True, False

##seeded
#True, False

##coop
#True, False

#customMusic
#True, False

def extractCharacter(name):
    names = ['all char', 'story mode', 'aria', 'bard', 'bolt',
            'coda', 'dorian', 'dove', 'eli', 'melody', 'monk']
    for i in names:
        if i in name:
            return i
    if checkCadence(name):
        return 'cadence'
    return None


def checkCadence(name):
    delete = ['hardcore', 'seeded', 'deathless',
            'speedrun', 'co-op', 'custom', ' ', '_prod', '_dev', 'dlc']
    for i in delete:
        name = name.replace(i, '')
    return name == ''


def checkSeeded(name):
    return 'seeded' in name


def checkDLC(name):
    return 'dlc' in name


def checkCoop(name):
    return 'co-op' in name


def checkCustomMusic(name):
    return 'custom' in name


def extractMode(name):
    if '/' in name:
        return 'daily'
    if 'speedrun' in name and 'deathless' in name:
        return None
    if 'deathless' in name:
        return 'deathless'
    if 'speedrun' in name:
        return 'speed'
    if 'hardcore' in name:
        return 'score'
    return None


def extractAvailability(name):
    if '_dev' in name:
        return 'dev'
    if '_prod'in name:
        return 'prod'
    return 'normal'

class steam_board:

    def __init__(self, index_entry):
        name = index_entry['name'].lower()

        self._availability = extractAvailability(name)
        self._character = extractCharacter(name)
        self._mode = extractMode(name)
        self._date = self.extractDate(name)
        self._seeded = checkSeeded(name)
        self._coop = checkCoop(name)
        self._customMusic = checkCustomMusic(name)
        self._dlc = checkDLC(name)

        self.name = self.nice_name()
        self._name = name
        self._url = index_entry['url']

        if self.toofzSupport():
            self.url = self.toofzUrl()
        else:
            self.url = None


    def nice_name(self):
        ##TODO: Make up a pretty solution for all boards and write/implement
        if self.daily():
            return str(self._date)
        if self._character == None or self._mode == None:
            return 'None'
        result = self._character
        if self._customMusic:
            result += ' custom music'
        if self._coop:
            result += ' co-op'
        if self._seeded:
            result += ' seeded'
        result += ' ' + self._mode
        if self._dlc:
            result += ' Amplified'
        return result.title()

    def __str__(self):
        return self.name

    def __repr__(self):
        name = ''
        name += 'DLC: ' + str(self._dlc) + '\n'
        name += 'character: ' + str(self._character) + '\n'
        name += 'mode: ' + str(self._mode) + '\n'
        name += 'seeded: ' + str(self._seeded) + '\n'
        name += 'coop: ' + str(self._coop) + '\n'
        name += 'customMusic: ' + str(self._customMusic)
        return name


    def daily(self):
        return self._mode == 'daily'


    def extractDate(self, name):
        if not self.daily():
            return None
        name = name.replace('_dev', '')
        name = name.replace('_prod', '')
        sp = name.split()[0]
        sp = sp.split('/')
        return datetime.date(int(sp[2]), int(sp[1]), int(sp[0]))


    def maxLeaderboardEntries(self):
        #if self._customMusic:
            #return 1
        if self._coop:
            return 3
        if self._seeded:
            return 5
        if self._mode == 'deathless':
            return 5
        if self._mode == 'score':
            return 5
        if self._mode == 'speed':
            return 5
        if self._mode == 'daily':
            return 3
        return None

    def maxCompareEntries(self):
        return 100

    def include(self):

        if self._availability != 'prod':
            return False


        if self._customMusic:
            return False
        if self._coop and self._seeded:
            return False
        if self._seeded and self._mode == 'deathless':
            return False
        if self._mode == 'daily':
            return False
        if self._character == None:
            return False
        if self._coop:
            return False


        if self._mode == 'deathless':
            if self._character == 'all char' or self._character == 'story mode':
                return False

        if self._seeded:
            if self._character == 'all char' or self._character == 'story mode':
                return False
            return True # <3 Grimy
        if self._mode != None:
            return True
        return False


    def toofzChar(self, char):
        if char == 'all char':
            return 'all'
        if char == 'story mode':
            return 'story'
        return char


    def toofzMode(self, mode):
        #mode = mode.replace('score', 'hardcore')
        return mode


    def toofzSupport(self):
        if self._coop or self._customMusic:
            return False
        if self._mode == None:
            return False
        return True


    def toofzUrl(self):
        if self._dlc:
            base = 'http://crypt.toofz.com/leaderboards/amplified/'
        else:
            base = 'http://crypt.toofz.com/leaderboards/'
        if self.daily():
            return base + 'Daily/' + self._date.strftime('%Y/%m/%d/')
        #http://crypt.toofz.com/Leaderboards/Daily/2015/05/27
        char = self.toofzChar(self._character)
        mode = self.toofzMode(self._mode)
        if self._seeded:
            return base + '%s/seeded%s'%(char, mode)
        return base + '%s/%s'%(char, mode)

    def parseResponse(self, response):
        return nsb_database.xmlToList(response, 'leaderboard')


    def getTwitterHandle(self, person, twitter):
        return nsb_steam.getTwitterHandle(int(person['steam_id']), twitter)



    def entriesToReportOnPointsDiff(self):
        return 5

    def entriesToReportOnRankDiff(self):
        return 10

    def entriesToPrivateReportOnPointsDiff(self):
        return 100

    def entriesToPrivateReportOnRankDiff(self):
        return 100

    def report(self, person, hist, twitter):

        if hist is None:
            if person['rank'] <= self.entriesToReportOnRankDiff():
                return True
            #Check for private tweet
            if person['rank'] <= self.entriesToPrivateReportOnRankDiff():
                twitter_handle = self.getTwitterHandle(person, twitter)
                if twitter_handle:
                    return True
            return False

        #If the person haven't improved points, return false
        if float(hist['points']) >= person['points']:
            return False

        #Check for public tweet
        if person['rank'] <= self.entriesToReportOnRankDiff():
            return True

        #Check for private tweet
        if person['rank'] <= self.entriesToPrivateReportOnRankDiff():
            twitter_handle = self.getTwitterHandle(person, twitter)
            if twitter_handle:
                person['twitter_username'] = twitter_handle
                return True


        return False

    def formatPoints(self, points):
        points = int(points)
        if self._mode == 'speed':
            time = nsb_format_points.scoreAsMilliseconds(points)
            return nsb_format_points.formatTime(time)
        if self._mode == 'score':
            return str(int(points))
        if self._mode == 'deathless':
            return nsb_format_points.formatProgress(points)

    def relativePoints(self, points, prevPoints):
        points = int(points)
        prevPoints = int(prevPoints)
        if self._mode == 'speed':
            points = nsb_format_points.scoreAsMilliseconds(points)
            prevPoints = nsb_format_points.scoreAsMilliseconds(prevPoints)
            return nsb_format_points.relativeTime(points, prevPoints)
        if self._mode == 'score':
            return  nsb_format_points.relativeScore(points, prevPoints)
        if self._mode == 'deathless':
            return nsb_format_points.relativeProgress(points, prevPoints)

    def impossiblePoints(self, person):
        if self._mode == 'score' and person['points'] > 200000:
            return True
        return False

    def unit(self):
        if self._mode == 'score':
            return 'gold'
        return None

    def pre_unit(self):
        if self._mode == 'deathless':
            return 'streak'
        if self._mode == 'speed':
            return 'time'
        return None

    def getUrl(self, person):
        if self._mode == 'daily':
            return self.url
        return self.url + '?id=' + str(person['steam_id'])
