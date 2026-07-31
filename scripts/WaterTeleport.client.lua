--[[
	WATER TOUCH → 15s → TELEPORT TO spawn1

	Put this LocalScript here:

	StarterPlayer
	└─ StarterPlayerScripts
	   └─ WaterTeleport   ← LocalScript (paste code below)

	Hierarchy it expects:

	Workspace
	└─ cliff
	   ├─ Water Blocks
	   │  └─ water          ← part you touch (CanTouch = true)
	   └─ spawn
	      └─ spawn1         ← teleport target (Anchored = true)

	Behavior:
	- Touch water → 15 second timer starts
	- Leave water before 15s → timer cancels
	- Stay in water for full 15s → teleport to spawn1
]]

local Players = game:GetService("Players")

local player = Players.LocalPlayer

local WATER_TIME = 15 -- seconds before teleport

local cliff = workspace:WaitForChild("cliff")
local water = cliff:WaitForChild("Water Blocks"):WaitForChild("water")
local spawn1 = cliff:WaitForChild("spawn"):WaitForChild("spawn1")

-- Touched only fires if CanTouch is on
water.CanTouch = true

local timerThread = nil
local touching = 0 -- how many of the player's parts are currently touching water

local function isMyCharacterPart(hit)
	local character = player.Character
	if not character then
		return false
	end
	return hit:IsDescendantOf(character)
end

local function cancelTimer()
	if timerThread then
		task.cancel(timerThread)
		timerThread = nil
	end
end

local function teleportToSpawn()
	local character = player.Character
	if not character then
		return
	end
	character:PivotTo(spawn1.CFrame * CFrame.new(0, spawn1.Size.Y / 2 + 3, 0))
end

local function startTimer()
	if timerThread then
		return -- already counting
	end

	timerThread = task.delay(WATER_TIME, function()
		timerThread = nil
		if touching > 0 then
			teleportToSpawn()
			touching = 0
		end
	end)
end

water.Touched:Connect(function(hit)
	if not isMyCharacterPart(hit) then
		return
	end

	touching += 1
	if touching == 1 then
		startTimer()
	end
end)

water.TouchEnded:Connect(function(hit)
	if not isMyCharacterPart(hit) then
		return
	end

	touching = math.max(0, touching - 1)
	if touching == 0 then
		cancelTimer()
	end
end)

-- Reset if character respawns / dies mid-timer
player.CharacterAdded:Connect(function()
	cancelTimer()
	touching = 0
end)

print("[WaterTeleport] Ready — stay in water", WATER_TIME, "seconds to return to spawn1")
