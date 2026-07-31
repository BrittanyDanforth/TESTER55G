--[[
	SWIMMABLE WATER + 15s → TELEPORT TO spawn1

	Put this LocalScript here (replace your old WaterTeleport code):

	StarterPlayer
	└─ StarterPlayerScripts
	   └─ WaterTeleport   ← LocalScript

	Hierarchy:

	Workspace
	└─ cliff
	   ├─ Water Blocks
	   │  └─ water (and any other water parts)
	   └─ spawn
	      └─ spawn1

	PART SETTINGS (script sets these automatically):
	- CanCollide = false   (so you enter the water, not stand on it)
	- CanTouch = true
	- Anchored = true

	Behavior:
	- Enter water → you swim (buoyancy + swim state)
	- Stay 15 seconds → teleport to spawn1
	- Leave early → timer cancels
]]

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

local player = Players.LocalPlayer

local WATER_TIME = 15
-- ~1.0 = float in place, a bit under 1 = slow sink, above 1 = rise
local BUOYANCY = 1.05
local WATER_DRAG = 0.92 -- slows you down in water (1 = no drag)

local cliff = workspace:WaitForChild("cliff")
local waterFolder = cliff:WaitForChild("Water Blocks")
local spawn1 = cliff:WaitForChild("spawn"):WaitForChild("spawn1")

-- All BaseParts inside Water Blocks become swim volumes
local waterParts = {}

local function setupWaterPart(part)
	if not part:IsA("BasePart") then
		return
	end
	part.Anchored = true
	part.CanCollide = false -- MUST be false or you stand on top / can't swim in
	part.CanTouch = true
	part.CanQuery = true
	table.insert(waterParts, part)
end

for _, child in waterFolder:GetDescendants() do
	setupWaterPart(child)
end

waterFolder.DescendantAdded:Connect(setupWaterPart)

local overlapParams = OverlapParams.new()
overlapParams.FilterType = Enum.RaycastFilterType.Include

local timerThread = nil
local wasInWater = false
local swimForce = nil
local swimAttachment = nil
local heartbeatConn = nil

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
	cancelTimer()
	wasInWater = false
	if swimForce then
		swimForce.Force = Vector3.zero
	end
	character:PivotTo(spawn1.CFrame * CFrame.new(0, spawn1.Size.Y / 2 + 3, 0))
end

local function startTimer()
	if timerThread then
		return
	end
	timerThread = task.delay(WATER_TIME, function()
		timerThread = nil
		if wasInWater then
			teleportToSpawn()
		end
	end)
end

local function isCharacterInWater(character)
	overlapParams.FilterDescendantsInstances = { character }
	for _, waterPart in waterParts do
		if waterPart.Parent and #workspace:GetPartsInPart(waterPart, overlapParams) > 0 then
			return true
		end
	end
	return false
end

local function cleanupSwim()
	cancelTimer()
	wasInWater = false
	if heartbeatConn then
		heartbeatConn:Disconnect()
		heartbeatConn = nil
	end
	if swimForce then
		swimForce:Destroy()
		swimForce = nil
	end
	if swimAttachment then
		swimAttachment:Destroy()
		swimAttachment = nil
	end
end

local function setupCharacter(character)
	cleanupSwim()

	local humanoid = character:WaitForChild("Humanoid")
	local root = character:WaitForChild("HumanoidRootPart")

	humanoid:SetStateEnabled(Enum.HumanoidStateType.Swimming, true)

	swimAttachment = Instance.new("Attachment")
	swimAttachment.Name = "WaterSwimAttachment"
	swimAttachment.Parent = root

	swimForce = Instance.new("VectorForce")
	swimForce.Name = "WaterBuoyancy"
	swimForce.Attachment0 = swimAttachment
	swimForce.RelativeTo = Enum.ActuatorRelativeTo.World
	swimForce.ApplyAtCenterOfMass = true
	swimForce.Force = Vector3.zero
	swimForce.Parent = root

	heartbeatConn = RunService.Heartbeat:Connect(function()
		if not character.Parent or humanoid.Health <= 0 then
			return
		end

		local inWater = isCharacterInWater(character)

		if inWater then
			-- Keep swim state active (Part water is not Terrain water)
			humanoid:ChangeState(Enum.HumanoidStateType.Swimming)

			-- Buoyancy counters gravity so you float / swim instead of falling through
			local mass = root.AssemblyMass
			swimForce.Force = Vector3.new(0, mass * workspace.Gravity * BUOYANCY, 0)

			-- Soft drag so movement feels like water
			local v = root.AssemblyLinearVelocity
			root.AssemblyLinearVelocity = v * WATER_DRAG

			if not wasInWater then
				wasInWater = true
				startTimer()
			end
		else
			swimForce.Force = Vector3.zero

			if wasInWater then
				wasInWater = false
				cancelTimer()
			end
		end
	end)
end

if player.Character then
	setupCharacter(player.Character)
end

player.CharacterAdded:Connect(setupCharacter)

print("[WaterTeleport] Swim ready — 15s in water returns you to spawn1")
