--[[
	FALL DAMAGE + BLACK SCREEN (no text)

	Put this LocalScript here:

	StarterPlayer
	└─ StarterPlayerScripts
	   └─ FallDamage   ← LocalScript (paste code below)

	What it does:
	- Damages you when you fall from a high place
	- Screen fades to solid black (no words, no UI text)
	- On death, stays black until you respawn
]]

local Players = game:GetService("Players")
local TweenService = game:GetService("TweenService")

local player = Players.LocalPlayer

-- Tune these
local MIN_FALL_SPEED = 50 -- studs/sec before damage starts
local DAMAGE_PER_SPEED = 0.8 -- how hard each unit of speed hits
local MAX_DAMAGE = 100
local BLACK_FADE_IN = 0.25
local BLACK_HOLD = 0.35
local BLACK_FADE_OUT = 0.5

-- Black screen (no text)
local screenGui = Instance.new("ScreenGui")
screenGui.Name = "FallDamageBlackout"
screenGui.IgnoreGuiInset = true
screenGui.ResetOnSpawn = false
screenGui.DisplayOrder = 1000
screenGui.Parent = player:WaitForChild("PlayerGui")

local black = Instance.new("Frame")
black.Name = "Black"
black.Size = UDim2.fromScale(1, 1)
black.Position = UDim2.fromScale(0, 0)
black.BackgroundColor3 = Color3.new(0, 0, 0)
black.BackgroundTransparency = 1
black.BorderSizePixel = 0
black.Parent = screenGui

local fadeInInfo = TweenInfo.new(BLACK_FADE_IN, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
local fadeOutInfo = TweenInfo.new(BLACK_FADE_OUT, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)

local blackoutToken = 0

local function flashBlack(stayUntilRespawn)
	blackoutToken += 1
	local token = blackoutToken

	TweenService:Create(black, fadeInInfo, { BackgroundTransparency = 0 }):Play()

	if stayUntilRespawn then
		return
	end

	task.delay(BLACK_FADE_IN + BLACK_HOLD, function()
		if token ~= blackoutToken then
			return
		end
		TweenService:Create(black, fadeOutInfo, { BackgroundTransparency = 1 }):Play()
	end)
end

local function clearBlack()
	blackoutToken += 1
	TweenService:Create(black, fadeOutInfo, { BackgroundTransparency = 1 }):Play()
end

local function setupCharacter(character)
	local humanoid = character:WaitForChild("Humanoid")
	local root = character:WaitForChild("HumanoidRootPart")

	local maxFallSpeed = 0
	local falling = false

	local stateConn = humanoid.StateChanged:Connect(function(_, newState)
		if newState == Enum.HumanoidStateType.Freefall then
			falling = true
			maxFallSpeed = 0
		elseif falling and (newState == Enum.HumanoidStateType.Landed or newState == Enum.HumanoidStateType.Running) then
			falling = false
			local impact = maxFallSpeed
			maxFallSpeed = 0

			if impact >= MIN_FALL_SPEED then
				local damage = math.clamp((impact - MIN_FALL_SPEED) * DAMAGE_PER_SPEED, 0, MAX_DAMAGE)
				if damage > 0 then
					flashBlack(false)
					humanoid:TakeDamage(damage)
				end
			end
		end
	end)

	local diedConn = humanoid.Died:Connect(function()
		flashBlack(true)
	end)

	-- Track downward speed while falling
	task.spawn(function()
		while character.Parent and humanoid.Health > 0 do
			if falling then
				local vy = -root.AssemblyLinearVelocity.Y
				if vy > maxFallSpeed then
					maxFallSpeed = vy
				end
			end
			task.wait()
		end
	end)

	-- Cleanup when character is removed / respawns
	character.AncestryChanged:Connect(function(_, parent)
		if parent then
			return
		end
		stateConn:Disconnect()
		diedConn:Disconnect()
	end)
end

if player.Character then
	setupCharacter(player.Character)
end

player.CharacterAdded:Connect(function(character)
	clearBlack()
	setupCharacter(character)
end)
