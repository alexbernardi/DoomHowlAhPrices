-- Create addon namespace
local AddonName, Addon = ...
Addon.version = GetAddOnMetadata(AddonName, "Version") or "1.0"

Addon.GET_ALL_COOLDOWN = 15 * 60  -- 15 minutes in seconds

-- Main addon frame for event handling
local MainFrame = CreateFrame("Frame")

-- Initialize function
function Addon:Initialize()
    -- Register events
    MainFrame:RegisterEvent("ADDON_LOADED")
    MainFrame:RegisterEvent("PLAYER_LOGIN")
    MainFrame:RegisterEvent("AUCTION_HOUSE_SHOW")
    MainFrame:RegisterEvent("AUCTION_HOUSE_CLOSED") 
    MainFrame:RegisterEvent("AUCTION_ITEM_LIST_UPDATE")
    
    -- Set up event handler
    MainFrame:SetScript("OnEvent", function(self, event, ...)
        if event == "ADDON_LOADED" and ... == AddonName then
            Addon:OnAddonLoaded()
        elseif event == "PLAYER_LOGIN" then
            Addon:OnPlayerLogin()
        elseif event == "AUCTION_HOUSE_SHOW" then
            Addon:OnAuctionHouseShow()
        elseif event == "AUCTION_HOUSE_CLOSED" then
            Addon:OnAuctionHouseClosed()  -- Add this handler
        elseif event == "AUCTION_ITEM_LIST_UPDATE" then
            Addon:OnAuctionItemListUpdate()
        end
    end)
    
    print("|cff33ff99" .. AddonName .. "|r: Initialized! Type /simpleAH for options.")
end

function Addon:OnAuctionHouseClosed()
    -- Clean up any UI elements
    Addon.isScanning = false
    Addon.pendingGetAllScan = false
    
    if Addon.scanTimer then
        Addon.scanTimer:Cancel()
        Addon.scanTimer = nil
    end
end

-- Event handlers
function Addon:OnAddonLoaded()
    -- Initialize saved variables
    if not SimpleAHScanData then
        SimpleAHScanData = {
            lastGetAllScan = 0,  -- Server time of last scan
            scans = {}           -- Table to store historical scan data
        }
    end
    
    -- Ensure scans table exists (for upgrades from older versions)
    if not SimpleAHScanData.scans then
        SimpleAHScanData.scans = {}
    end

    -- Add auto-reload setting if upgrading
    if SimpleAHScanData.autoReload == nil then
        SimpleAHScanData.autoReload = false
    end

    -- Initialize scan state
    Addon.isScanning = false
    Addon.pendingGetAllScan = false

    -- Initialize saved variables or settings here if needed
    print("|cff33ff99" .. AddonName .. "|r: Loaded version " .. Addon.version)
end

function Addon:OnPlayerLogin()
    -- Do things when player logs in
end

function Addon:OnAuctionHouseShow()
    -- Display a message when talking to an auctioneer
    DEFAULT_CHAT_FRAME:AddMessage("|cff33ff99" .. AddonName .. "|r: You are now talking to an auctioneer!")
    
    -- Create the scan button if it doesn't exist yet
    if not Addon.scanButton then
        Addon:CreateScanButton()
    end
end

-- Add this function to update the button with cooldown info
function Addon:UpdateScanButtonCooldown()
    if not Addon.scanButton then return end
    
    local currentTime = time()
    local timeElapsed = currentTime - SimpleAHScanData.lastGetAllScan
    
    if timeElapsed < Addon.GET_ALL_COOLDOWN then
        -- Still on cooldown
        local timeRemaining = math.ceil(Addon.GET_ALL_COOLDOWN - timeElapsed)
        local minutes = math.floor(timeRemaining / 60)
        local seconds = timeRemaining % 60
        
        Addon.scanButton:SetText(string.format("Scan (%d:%02d)", minutes, seconds))
        Addon.scanButton:Disable()
    else
        Addon.scanButton:SetText("Scan")
    end
end

function Addon:CreateScanButton()
    -- Create the button
    local button = CreateFrame("Button", "SimpleAHScanButton", AuctionFrameBrowse, "UIPanelButtonTemplate")
    button:SetSize(90, 22)
    button:SetText("Scan")
    button:SetPoint("BOTTOMRIGHT", AuctionFrameBrowse, "BOTTOMRIGHT", -222, 14)
    
    -- Set click handler
    button:SetScript("OnClick", function()
        Addon:StartAuctionScan()
    end)
    
    -- Update timer
    button:SetScript("OnUpdate", function(self, elapsed)
        Addon.updateElapsed = (Addon.updateElapsed or 0) + elapsed
        if Addon.updateElapsed > 1 then -- Update once per second
            Addon:UpdateScanButtonCooldown()
            Addon.updateElapsed = 0
        end
    end)
    
    -- Store reference
    Addon.scanButton = button
    
    -- Initial update
    Addon:UpdateScanButtonCooldown()
end

function Addon:StartAuctionScan()
    local currentTime = time()  -- Server time in seconds
    local useGetAll = true  -- Set to true if you want to use getAll

    -- Check if we want to use getAll and if it's on cooldown
    if useGetAll then
        local timeElapsed = currentTime - SimpleAHScanData.lastGetAllScan
        if timeElapsed < Addon.GET_ALL_COOLDOWN then
            -- Still on cooldown
            local timeRemaining = math.ceil(Addon.GET_ALL_COOLDOWN - timeElapsed)
            local minutes = math.floor(timeRemaining / 60)
            local seconds = timeRemaining % 60
            print("|cff33ff99" .. AddonName .. "|r: GetAll scan on cooldown. Available in " .. minutes .. "m " .. seconds .. "s")
            return
        end
    end

    print("|cff33ff99" .. AddonName .. "|r: Starting auction scan...")
    -- Play a sound
    PlaySound(SOUNDKIT.MONEY_FRAME_OPEN)

    -- Store that we're currently scanning
    Addon.isScanning = true

    -- Set the pending GetAll scan flag if we're using GetAll
    if useGetAll then
        Addon.pendingGetAllScan = true
    end

    -- Update button text/state to show scanning is in progress
    if Addon.scanButton then
        Addon.scanButton:SetText("Scanning...")
        Addon.scanButton:Disable()
    end

    -- Query the first page of the auction house with no filters
    -- QueryAuctionItems(name, minLevel, maxLevel, invTypeIndex, classIndex, subclassIndex, page, isUsable, qualityIndex, getAll, exactMatch)
    QueryAuctionItems("", 0, 0, 0, 0, 0, 0, 0, 0, useGetAll, false)
    print("|cff33ff99" .. AddonName .. "|r: Query sent, waiting for results...")

    -- Set up a timeout in case we don't get results
    if Addon.scanTimer then
        Addon.scanTimer:Cancel()
    end

    Addon.scanTimer = C_Timer.NewTimer(100, function()
        if Addon.isScanning then
            print("|cff33ff99" .. AddonName .. "|r: Scan timeout - no results received.")
            Addon.isScanning = false
            Addon.pendingGetAllScan = false
            if Addon.scanButton then
                Addon.scanButton:SetText("Scan")
                Addon.scanButton:Enable()
            end
        end
    end)
end

-- Handle auction updates
function Addon:OnAuctionItemListUpdate()
    -- Only process if we're scanning
    if not Addon.isScanning then return end

    -- Reset button state
    if Addon.scanButton then
        Addon.scanButton:SetText("Scan")
        Addon.scanButton:Enable()
    end

    -- If this was a getAll scan, update the saved timestamp
    if Addon.pendingGetAllScan then
        SimpleAHScanData.lastGetAllScan = time()
        Addon.pendingGetAllScan = false
        print("|cff33ff99" .. AddonName .. "|r: GetAll scan complete. Next scan available in 15 minutes.")
    end
    
    -- Reset scanning state
    Addon.isScanning = false
    
    -- Get the number of auction items
    local numBatchAuctions, totalAuctions = GetNumAuctionItems("list")
    print("|cff33ff99" .. AddonName .. "|r: Found " .. numBatchAuctions .. " items on this page (out of " .. totalAuctions .. " total)")

    -- Create a new scan record
    local currentTime = time()
    local realmName = GetRealmName()
    local faction = UnitFactionGroup("player")

    local scanData = {
        timestamp = currentTime,
        realm = realmName,
        faction = faction,
        data = {}
    }
    
    -- Process each auction item
    for i = 1, numBatchAuctions do
        local name, texture, count, quality, canUse, level, _, minBid, 
              minIncrement, buyoutPrice, bidAmount, highBidder, bidderFullName, 
              owner, ownerFullName = GetAuctionItemInfo("list", i)
        
        local itemLink = GetAuctionItemLink("list", i)
        local itemId = nil
        
        -- Extract itemId from itemLink if available
        if itemLink then
            itemId = itemLink:match("item:(%d+)")
        end
        
        -- Only save items with valid data
        if name and itemId then
            -- Calculate prices per item
            local minBidPerItem = minBid and (minBid / count) or 0
            local buyoutPerItem = buyoutPrice and (buyoutPrice / count) or 0
            
            -- Create item record
            local auctionRecord = {
                id = itemId,
                name = name,
                link = itemLink,
                count = count,
                quality = quality,
                level = level,
                minBid = minBid,
                minBidPerItem = minBidPerItem,
                buyout = buyoutPrice,
                buyoutPerItem = buyoutPerItem,
                owner = owner
            }
            
            -- Add to scan data
            table.insert(scanData.data, auctionRecord)
        end
    end
    -- Add the scan to saved data
    table.insert(SimpleAHScanData.scans, scanData)

    -- To prevent too much data accumulating, keep only last 10 scans
    while #SimpleAHScanData.scans > 10 do
        table.remove(SimpleAHScanData.scans, 1)
    end

    -- Print summary
    print("|cff33ff99" .. AddonName .. "|r: Saved scan data for " .. #scanData.data .. " items")
    
    -- Check if we should auto-reload
    if SimpleAHScanData.autoReload then
        print("|cff33ff99" .. AddonName .. "|r: Auto-reloading UI to save scan data...")
        C_Timer.After(1, function()
            ReloadUI()
        end)
    end

    PlaySound(SOUNDKIT.AUCTION_WINDOW_CLOSE)
end

-- Slash command handler
local function HandleSlashCommands(msg)
    if msg == "help" or msg == "" then
        print("|cff33ff99" .. AddonName .. "|r: Available commands:")
        print("  /simpleAH scans - Show number of saved scans")
        print("  /simpleAH last - Show summary of last scan")
        print("  /simpleAH purge - Purges all saved scan data (Use with caution!)")
        print("  /simpleAH reload - Toggle auto-reload after scans (currently: " .. 
          (SimpleAHScanData.autoReload and "ON" or "OFF") .. ")")
        -- Add more command descriptions here
    elseif msg == "scans" then
        local numScans = #SimpleAHScanData.scans
        print("|cff33ff99" .. AddonName .. "|r: You have " .. numScans .. " saved scans.")
        if numScans > 0 then
            local latestScan = SimpleAHScanData.scans[numScans]
            print("Latest scan: " .. date("%Y-%m-%d %H:%M:%S", latestScan.timestamp) .. 
                  " on " .. latestScan.realm .. " (" .. latestScan.faction .. ") with " .. 
                  #latestScan.data .. " items")
        end
    elseif msg == "reload" or msg == "autoreload" then
        SimpleAHScanData.autoReload = not SimpleAHScanData.autoReload
        if SimpleAHScanData.autoReload then
            print("|cff33ff99" .. AddonName .. "|r: Auto-reload after scan ENABLED")
        else
            print("|cff33ff99" .. AddonName .. "|r: Auto-reload after scan DISABLED")
        end
    elseif msg == "last" then
        local numScans = #SimpleAHScanData.scans
        if numScans > 0 then
            local latestScan = SimpleAHScanData.scans[numScans]
            print("|cff33ff99" .. AddonName .. "|r: Latest scan from " .. date("%Y-%m-%d %H:%M:%S", latestScan.timestamp))
            print("Realm: " .. latestScan.realm .. " - Faction: " .. latestScan.faction)
            print("Total items: " .. #latestScan.data)
            
            -- Show a few sample items
            print("Sample items:")
            local max = math.min(5, #latestScan.data)
            for i = 1, max do
                local item = latestScan.data[i]
                print("  " .. item.link .. " x" .. item.count .. " - " .. 
                      GetCoinTextureString(item.buyoutPerItem))
            end
        else
            print("|cff33ff99" .. AddonName .. "|r: No saved scans found.")
        end
    elseif msg == "purge" then
        SimpleAHScanData.scans = {}
        print("|cff33ff99" .. AddonName .. "|r: All scan data purged.")
    else
        print("|cff33ff99" .. AddonName .. "|r: Unknown command. Type /simpleAH help for available commands.")
    end
end

-- Register slash commands
SLASH_SIMPLEAH1 = "/simpleAH"
SlashCmdList["SIMPLEAH"] = HandleSlashCommands

-- Initialize the addon
Addon:Initialize()