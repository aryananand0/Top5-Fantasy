import { cn } from '@/lib/cn'

function Bone({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        'rounded-lg bg-paper-dark animate-pulse',
        className,
      )}
    />
  )
}

export function DashboardSkeleton() {
  return (
    <div className="flex flex-col gap-4">
      {/* Banner */}
      <Bone className="h-28 rounded-2xl" />

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-3">
        <Bone className="h-20" />
        <Bone className="h-20" />
        <Bone className="h-20" />
      </div>

      {/* Captain cards */}
      <Bone className="h-6 w-32" />
      <div className="grid grid-cols-2 gap-3">
        <Bone className="h-32 rounded-2xl" />
        <Bone className="h-32 rounded-2xl" />
      </div>

      {/* Actions */}
      <div className="grid grid-cols-2 gap-3">
        <Bone className="h-10 rounded-xl" />
        <Bone className="h-10 rounded-xl" />
      </div>

      {/* Fixtures */}
      <Bone className="h-6 w-40" />
      <div className="flex flex-col gap-2">
        <Bone className="h-14 rounded-2xl" />
        <Bone className="h-14 rounded-2xl" />
        <Bone className="h-14 rounded-2xl" />
      </div>
    </div>
  )
}
