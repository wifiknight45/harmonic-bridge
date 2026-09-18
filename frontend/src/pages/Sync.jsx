import PlaylistConverter from '../components/PlaylistConverter'
import AccountStatus from '../components/AccountStatus'

export default function Sync() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold md:text-3xl">Sync your library</h1>
        <p className="mt-1 text-white/55">
          Move playlists across platforms without the spreadsheet grind.
        </p>
      </div>
      <AccountStatus />
      <PlaylistConverter />
    </div>
  )
}
