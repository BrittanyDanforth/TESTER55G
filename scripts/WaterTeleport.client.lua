--[[
	SWIMMABLE WATER + 15s → TELEPORT TO spawn1

	DELETE everything in your LocalScript named "water", then paste
	ONLY the code BELOW this comment block (or paste this whole file).

	Location:
	StarterPlayer → StarterPlayerScripts → water
]]

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

local player = Players.LocalPlayer

local WATER_TIME = 15
local BUOYANCY = 1.05
local WATER_DRAG = 0.92

local cliff = workspace:WaitForChild("cliff")
local waterFolder = cliff:WaitForChild("Water Blocks")
local spawn1 = cliff:WaitForChild("spawn"):WaitForChild("spawn1")

local waterParts = {}

local function setupWaterPart(part)
	if part:IsA("BasePart") then
		part.Anchored = true
		part.CanCollide = false
		part.CanTouch = true
		part.CanQuery = true
		table.insert(waterParts, part)
	end
end

for _, child in ipairs(waterFolder:GetDescendants()) do
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
	for _, waterPart in ipairs(waterParts) do
		if waterPart.Parent then
			local hits = workspace:GetPartsInPart(waterPart, overlapParams)
			if #hits > 0 then
				return true
			end
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
			humanoid:ChangeState(Enum.HumanoidStateType.Swimming)
			swimForce.Force = Vector3.new(0, root.AssemblyMass * workspace.Gravity * BUOYANCY, 0)
			root.AssemblyLinearVelocity = root.AssemblyLinearVelocity * WATER_DRAG

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
