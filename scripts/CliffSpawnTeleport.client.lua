--[[
	WHY YOUR CLICK DID NOTHING
	1) LocalScripts inside Workspace do NOT run.
	   Your LocalScript under lobby > cliffchoosing > SurfaceGui > 1 never starts,
	   so Activated is never connected.
	2) Earlier paths were wrong. From your Explorer:

	Workspace
	├─ cliff
	│  └─ spawn
	│     └─ spawn1          ← teleport target
	└─ lobby                 ← sibling of cliff (NOT inside cliff)
	   └─ cliffchoosing
	      └─ SurfaceGui
	         └─ 1            ← the button (leave it here)

	SETUP
	1. DELETE the LocalScript that is currently under button "1".
	2. In Explorer go to:
	   StarterPlayer → StarterPlayerScripts
	3. Insert a LocalScript, name it CliffSpawnTeleport
	4. Paste EVERYTHING below this comment block into that LocalScript.
	5. On spawn1: set Anchored = true (CanCollide can stay off).
	6. Playtest (not just Edit), then click button "1".
]]

local Players = game:GetService("Players")

local player = Players.LocalPlayer

-- Button path (lobby is DIRECTLY under Workspace)
local playButton = workspace
	:WaitForChild("lobby")
	:WaitForChild("cliffchoosing")
	:WaitForChild("SurfaceGui")
	:WaitForChild("1")

-- Spawn path (spawn1 is under cliff, not Terrain)
local spawn1 = workspace
	:WaitForChild("cliff")
	:WaitForChild("spawn")
	:WaitForChild("spawn1")

local function teleportToSpawn()
	local character = player.Character or player.CharacterAdded:Wait()
	local hrp = character:FindFirstChild("HumanoidRootPart")
	if not hrp then
		character:WaitForChild("HumanoidRootPart", 5)
	end

	-- Slightly above spawn1 so you don't clip into the part
	character:PivotTo(spawn1.CFrame * CFrame.new(0, spawn1.Size.Y / 2 + 3, 0))
end

playButton.Activated:Connect(teleportToSpawn)

-- Debug: if you see this in Output when the game starts, the script is running
print("[CliffSpawnTeleport] Ready. Click button '1' to teleport to spawn1.")
