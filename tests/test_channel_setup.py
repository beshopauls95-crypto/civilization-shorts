import copy
import unittest
from unittest.mock import Mock
from src.channel_setup import run, branding_body

CID = "UC" + "x"*22
PROFILE = {"name":"أسرار الحضارات | Civilization Secrets","description_ar":"قصص موثقة. مشاهد تخيلية بالذكاء الاصطناعي.","keywords":["مصر القديمة","تاريخ"],"language":"ar","country":"EG"}

class ChannelSetupTests(unittest.TestCase):
    def api(self, channel):
        api=Mock()
        api.channels.return_value.list.return_value.execute.return_value={"items":[channel]}
        return api
    def channel(self):
        return {"id":CID,"snippet":{"title":PROFILE["name"]},"brandingSettings":{"channel":{"description":"old","unsubscribedTrailer":"old-trailer","trackingAnalyticsAccountId":"old-tracking"}}}
    def test_check_never_writes(self):
        api=self.api(self.channel())
        self.assertEqual(run(api,CID,PROFILE)["status"],"connected")
        api.channels.return_value.update.assert_not_called()
    def test_wrong_channel_never_writes(self):
        api=self.api(self.channel())
        with self.assertRaises(PermissionError):run(api,"UC"+"y"*22,PROFILE,"apply_profile")
        api.channels.return_value.update.assert_not_called()
    def test_personal_channel_never_rebranded(self):
        channel=self.channel();channel["snippet"]["title"]="حكاوى التاريخ"
        api=self.api(channel)
        with self.assertRaises(PermissionError):run(api,CID,PROFILE,"apply_profile")
        api.channels.return_value.update.assert_not_called()
    def test_preserves_other_mutable_settings(self):
        channel=self.channel();before=copy.deepcopy(channel)
        body=branding_body(channel,PROFILE)
        self.assertEqual(body["brandingSettings"]["channel"]["unsubscribedTrailer"],"old-trailer")
        self.assertEqual(body["brandingSettings"]["channel"]["trackingAnalyticsAccountId"],"old-tracking")
        self.assertEqual(channel,before)
    def test_failed_readback_not_success(self):
        api=self.api(self.channel())
        with self.assertRaises(RuntimeError):run(api,CID,PROFILE,"apply_profile")
    def test_update_verified(self):
        channel=self.channel();body=branding_body(channel,PROFILE)
        after={**channel,"brandingSettings":body["brandingSettings"]}
        api=self.api(channel)
        api.channels.return_value.list.return_value.execute.side_effect=[{"items":[channel]},{"items":[after]}]
        self.assertEqual(run(api,CID,PROFILE,"apply_profile")["status"],"profile_applied_verified")
    def test_unknown_fields_stop(self):
        channel=self.channel();channel["brandingSettings"]["channel"]["futureMutable"]="keep"
        with self.assertRaises(ValueError):branding_body(channel,PROFILE)
