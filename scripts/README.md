# Roblox scripts

## Cliff spawn teleport

Clicking button **1** did nothing for two reasons:

1. **LocalScripts do not run in Workspace.** The script under `lobby > cliffchoosing > SurfaceGui > 1` never starts.
2. **Wrong paths.** `lobby` and `cliff` are both direct children of `Workspace` (siblings). `spawn1` is at `Workspace.cliff.spawn.spawn1`, not under Terrain.

### Fix

1. Delete the LocalScript under button `1`.
2. Put `CliffSpawnTeleport.client.lua` contents into a new LocalScript at:

```
StarterPlayer
└─ StarterPlayerScripts
   └─ CliffSpawnTeleport   ← LocalScript here
```

3. Leave the button where it is:

```
Workspace
├─ lobby
│  └─ cliffchoosing
│     └─ SurfaceGui
│        └─ 1              ← button stays here
└─ cliff
   └─ spawn
      └─ spawn1            ← teleport target (Anchored = true)
```

4. Playtest and click **1**. You should see `[CliffSpawnTeleport] Ready...` in Output if the script started.

## Fall damage + black screen

Put `FallDamage.client.lua` into:

```
StarterPlayer
└─ StarterPlayerScripts
   └─ FallDamage   ← LocalScript here
```

Hard landings deal damage and fade the screen to solid black (no text). On death the screen stays black until respawn.

## Water touch → teleport to spawn1

Put `WaterTeleport.client.lua` into:

```
StarterPlayer
└─ StarterPlayerScripts
   └─ WaterTeleport   ← LocalScript here
```

Touch `cliff > Water Blocks > water` for **15 seconds** → teleport to `cliff > spawn > spawn1`.
Leave the water early and the timer cancels. On the `water` part, set **CanTouch = true**.
