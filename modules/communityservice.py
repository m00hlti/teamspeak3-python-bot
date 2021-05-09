from ts3API.TS3Connection import TS3QueryException
import ts3API.Events as Events

import Bot
import Moduleloader
from Moduleloader import *

channel_config = {}
channels_configured = []

@Moduleloader.setup
def setup_communityservice(ts3bot):
    """
    Setup the a community bot.
    :return:
    """  
    global bot
    global ts3conn
    bot = ts3bot
    ts3conn = bot.ts3conn

    global channel_config
    global channels_configured    
    channel_config = {int(k):v for k,v in config["channel_config"].items()}
    channels_configured = list(channel_config.keys())
    name = config["name"]

    global bots_home
    bots_home = config["botshome"]

@Moduleloader.channel_event(Events.ClientMovedSelfEvent, Events.ClientMovedEvent, )
def on_channel_join_event(evt):
    """
    Create a temporary channel 
    """

    # don't do it on your own, you dumbass :D
    if evt.client_id == int(bot.ts3conn.whoami()["client_id"]):
        logger.info("Don't do it, because it's me.")
        return

    if evt.target_channel_id in channels_configured:
        # Gather all information first:
        curr_ch_cfg = channel_config[evt.target_channel_id]

        # At least we need a name here.
        if "cname" in curr_ch_cfg:
            channel_name = curr_ch_cfg["cname"].format(curr_ch_cfg["currnum"])
        else:
            logger.warn("No channel name given for channel: " + str(evt.target_channel_id))
            return
       
        curr_ch_cfg["currnum"] += 1

        # Create Channel, move user to it, leave and join homechannel
        createAsSub = True
        if "createassub" in curr_ch_cfg:
            createAsSub = curr_ch_cfg["createassub"]
                
        if createAsSub == True:
            response = _get_channel_info(evt.target_channel_id)            
            cpid = evt.target_channel_id

            flags = []
            flags.append("channel_name=" + channel_name)
            if "ctopic" in curr_ch_cfg:    
                flags.append("channel_topic=" + curr_ch_cfg["ctopic"])
            if "cuser" in curr_ch_cfg:
                flags.append("channel_maxclients=" + str(curr_ch_cfg["cuser"]))
                flags.append("channel_flag_maxclients_unlimited=0")
            response = _channel_create(flags)
            cid = response["cid"]
            response = _channel_move(["cid=" + cid, "cpid=" + str(cpid)])

        else:
            response = _get_channel_info(evt.target_channel_id)
            cpid = response["pid"] 
            
            flags = []
            flags.append("channel_name=" + channel_name)
            if "ctopic" in curr_ch_cfg:    
                flags.append("channel_topic=" + curr_ch_cfg["ctopic"])
            if "cuser" in curr_ch_cfg:
                flags.append("channel_maxclients=" + str(curr_ch_cfg["cuser"]))
                flags.append("channel_flag_maxclients_unlimited=0")
            response = _channel_create(flags)

            cid = response["cid"]
            response = _channel_move(["cid=" + cid, "cpid=" + str(cpid), "order=" + str(evt.target_channel_id)])

        bot.ts3conn.clientmove(int(cid), evt.client_id)
        _bot_go_home()

def on_channel_message_event(_sender, **kw):
    pass

def _bot_go_home():
    """
    Just go to your homechannel boi.
    """
    bot.ts3conn.clientmove(bots_home, int(bot.ts3conn.whoami()["client_id"])) #bot.default_channel

def _channel_create(param):
    """
    Create a new channel.
    :param param: parameter used by channel_create qry
    :return: Response from query decoded to dict
    """
    return bot.ts3conn._parse_resp_to_dict(
        bot.ts3conn._send("channelcreate", param))

def _channel_move(param):
    """
    Move a new channel.
    :param param: parameter used by channel_move qry
    :return: Response from query decoded to dict
    """
    return bot.ts3conn._parse_resp_to_dict(
        bot.ts3conn._send("channelmove", param))

def _get_channel_info(cid):
    """
    Get channel info
    :param cid: Channel ID
    :return: Response from query decoded to dict
    """
    return bot.ts3conn._parse_resp_to_dict(
        bot.ts3conn._send("channelinfo", ["cid=" + str(cid)]))
    
