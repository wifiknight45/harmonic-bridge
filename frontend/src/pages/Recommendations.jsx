import HarmonicFlow from '../components/HarmonicFlow'
import TasteProfile from '../components/TasteProfile'

export default function Recommendations() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold md:text-3xl">Generate playlists</h1>
        <p className="mt-1 text-white/55">
          Seed from your taste, pull complementary tracks, sort by harmonic flow.
        </p>
      </div>
      <div className="grid gap-6 lg:grid-cols-5">
        <div className="lg:col-span-3">
          <HarmonicFlow />
        </div>
        <div className="lg:col-span-2">
          <TasteProfile />
        </div>
      </div>
    </div>
  )
}
