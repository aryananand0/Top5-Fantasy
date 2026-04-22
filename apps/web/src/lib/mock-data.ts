/**
 * Minimal mock data for placeholder UI.
 * Replace these with real API calls once the backend is connected.
 * Do not expand this file — it exists only to prevent empty-looking pages.
 */

export const mockUser = {
  displayName: 'Alex Freeman',
  teamName: 'Red Devils United',
  email: 'alex@example.com',
  totalPoints: 1847,
  rank: 15432,
  globalPercentile: 'Top 18%',
  budget: 4.2,
  teamValue: 103.8,
  favoriteLeague: 'PL',
}

export const mockGameweek = {
  number: 28,
  status: 'active' as 'active' | 'locked' | 'finished',
  deadline: 'Sat 8 Mar · 11:30',
  points: 64,
  averagePoints: 51,
  freeTransfers: 2,
}

export type MockPlayer = {
  id: string
  name: string
  club: string
  leagueCode: 'PL' | 'PD' | 'BL1' | 'SA' | 'FL1'
  position: 'GK' | 'DEF' | 'MID' | 'FWD'
  price: number
  gwPts: number
  totalPts: number
  isCaptain: boolean
  isVC: boolean
  isStarting: boolean
}

export const mockSquad: MockPlayer[] = [
  // ── Starting XI ──────────────────────────────────────────────────────────
  { id: '1',  name: 'Alisson',      club: 'Liverpool',   leagueCode: 'PL',  position: 'GK',  price: 5.5,  gwPts: 6,  totalPts: 112, isCaptain: false, isVC: false, isStarting: true  },
  { id: '2',  name: 'Trent A-A',    club: 'Liverpool',   leagueCode: 'PL',  position: 'DEF', price: 7.5,  gwPts: 9,  totalPts: 143, isCaptain: false, isVC: false, isStarting: true  },
  { id: '3',  name: 'Pedro Porro',  club: 'Spurs',       leagueCode: 'PL',  position: 'DEF', price: 5.5,  gwPts: 2,  totalPts: 89,  isCaptain: false, isVC: false, isStarting: true  },
  { id: '4',  name: 'Virgil',       club: 'Liverpool',   leagueCode: 'PL',  position: 'DEF', price: 6.0,  gwPts: 6,  totalPts: 118, isCaptain: false, isVC: false, isStarting: true  },
  { id: '5',  name: 'Robertson',    club: 'Liverpool',   leagueCode: 'PL',  position: 'DEF', price: 6.0,  gwPts: 6,  totalPts: 99,  isCaptain: false, isVC: false, isStarting: true  },
  { id: '6',  name: 'Salah',        club: 'Liverpool',   leagueCode: 'PL',  position: 'MID', price: 12.0, gwPts: 18, totalPts: 247, isCaptain: true,  isVC: false, isStarting: true  },
  { id: '7',  name: 'Bellingham',   club: 'Real Madrid', leagueCode: 'PD',  position: 'MID', price: 10.0, gwPts: 11, totalPts: 198, isCaptain: false, isVC: true,  isStarting: true  },
  { id: '8',  name: 'De Bruyne',    club: 'Man City',    leagueCode: 'PL',  position: 'MID', price: 10.0, gwPts: 3,  totalPts: 134, isCaptain: false, isVC: false, isStarting: true  },
  { id: '9',  name: 'Saka',         club: 'Arsenal',     leagueCode: 'PL',  position: 'MID', price: 9.0,  gwPts: 5,  totalPts: 156, isCaptain: false, isVC: false, isStarting: true  },
  { id: '10', name: 'Haaland',      club: 'Man City',    leagueCode: 'PL',  position: 'FWD', price: 12.5, gwPts: 12, totalPts: 221, isCaptain: false, isVC: false, isStarting: true  },
  { id: '11', name: 'Darwin N.',    club: 'Liverpool',   leagueCode: 'PL',  position: 'FWD', price: 8.0,  gwPts: 4,  totalPts: 97,  isCaptain: false, isVC: false, isStarting: true  },
  // ── Bench ────────────────────────────────────────────────────────────────
  { id: '12', name: 'Flekken',      club: 'Brentford',  leagueCode: 'PL',  position: 'GK',  price: 4.0,  gwPts: 2,  totalPts: 68,  isCaptain: false, isVC: false, isStarting: false },
  { id: '13', name: 'Pedro',        club: 'Barcelona',  leagueCode: 'PD',  position: 'DEF', price: 4.5,  gwPts: 0,  totalPts: 54,  isCaptain: false, isVC: false, isStarting: false },
  { id: '14', name: 'Kimmich',      club: 'Bayern',     leagueCode: 'BL1', position: 'MID', price: 7.5,  gwPts: 5,  totalPts: 122, isCaptain: false, isVC: false, isStarting: false },
  { id: '15', name: 'Lewandowski',  club: 'Barcelona',  leagueCode: 'PD',  position: 'FWD', price: 9.5,  gwPts: 8,  totalPts: 141, isCaptain: false, isVC: false, isStarting: false },
]

export const mockLeagues = [
  { id: 'office-rivals', name: 'Office Rivals',  members: 8,  userRank: 3, leader: 'Tom K.',   leaderPts: 1920, gwWinner: 'Tom K.',   gwWinnerPts: 78 },
  { id: 'college-mates', name: 'College Mates',  members: 12, userRank: 7, leader: 'Priya S.', leaderPts: 2104, gwWinner: 'Priya S.', gwWinnerPts: 91 },
]

export const mockLeagueStandings = [
  { rank: 1, displayName: 'Tom K.',   teamName: 'Red Rockets',     totalPts: 1920, gwPts: 78,  isMe: false },
  { rank: 2, displayName: 'Sarah L.', teamName: 'Barca Babes',     totalPts: 1904, gwPts: 55,  isMe: false },
  { rank: 3, displayName: 'Alex F.',  teamName: 'Red Devils Utd',  totalPts: 1847, gwPts: 64,  isMe: true  },
  { rank: 4, displayName: 'Ravi P.',  teamName: 'Foxes Forever',   totalPts: 1790, gwPts: 71,  isMe: false },
  { rank: 5, displayName: 'Emma C.',  teamName: 'Purple Haze',     totalPts: 1745, gwPts: 33,  isMe: false },
  { rank: 6, displayName: 'Luca M.',  teamName: 'Azzurri Dreams',  totalPts: 1710, gwPts: 49,  isMe: false },
  { rank: 7, displayName: 'Yemi A.',  teamName: 'Super Eagles FC', totalPts: 1688, gwPts: 62,  isMe: false },
  { rank: 8, displayName: 'Jin P.',   teamName: 'Seoul United',    totalPts: 1642, gwPts: 44,  isMe: false },
]

export const mockFixtures = [
  { id: 'f1', home: 'Man City',  away: 'Arsenal',   date: 'Sat 8 Mar',  time: '12:30', homeScore: null, awayScore: null },
  { id: 'f2', home: 'Liverpool', away: 'Chelsea',   date: 'Sat 8 Mar',  time: '15:00', homeScore: null, awayScore: null },
  { id: 'f3', home: 'Spurs',     away: 'Man Utd',   date: 'Sun 9 Mar',  time: '14:00', homeScore: null, awayScore: null },
  { id: 'f4', home: 'Newcastle', away: 'Wolves',    date: 'Sun 9 Mar',  time: '16:30', homeScore: null, awayScore: null },
  { id: 'f5', home: 'Brighton',  away: 'Villa',     date: 'Mon 10 Mar', time: '20:00', homeScore: null, awayScore: null },
  { id: 'f6', home: 'Real Madrid', away: 'Atletico', date: 'Sat 8 Mar', time: '21:00', homeScore: null, awayScore: null },
  { id: 'f7', home: 'Barcelona', away: 'Sevilla',   date: 'Sun 9 Mar',  time: '18:30', homeScore: null, awayScore: null },
]

export const mockPlayerHistory = [
  { gw: 27, pts: 12, opponent: 'vs Wolves (H)', minutes: 90 },
  { gw: 26, pts: 6,  opponent: 'vs Arsenal (A)', minutes: 90 },
  { gw: 25, pts: 15, opponent: 'vs Chelsea (H)', minutes: 90 },
  { gw: 24, pts: 2,  opponent: 'vs Villa (A)', minutes: 73 },
  { gw: 23, pts: 9,  opponent: 'vs Spurs (H)', minutes: 90 },
]
