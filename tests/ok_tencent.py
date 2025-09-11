#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Administrator
#
# Created:     11/09/2025
# Copyright:   (c) Administrator 2025
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models
SecretId = "AKIDEcv7B7gIm9PXefYJxSp397xgInAQYYSF"
SecretKey = "iJm8NTSI1lQ3Xu7CMWYTIzYzKXclniVA"
class Translator:
    def __init__(self, from_lang, to_lang):
        self.from_lang = from_lang
        self.to_lang = to_lang

    def translate(self, text):
        try:
            cred = credential.Credential(SecretId, SecretKey)
            httpProfile = HttpProfile()
            httpProfile.endpoint = "tmt.tencentcloudapi.com"

            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = tmt_client.TmtClient(cred, "ap-beijing", clientProfile)

            req = models.TextTranslateRequest()
            req.SourceText = text
            req.Source = self.from_lang
            req.Target = self.to_lang
            req.ProjectId = 0

            resp = client.TextTranslate(req)
            return resp.TargetText

        except TencentCloudSDKException as err:
            return err

if __name__ == '__main__':
    translator = Translator(from_lang="en", to_lang="zh")
    print(translator.translate("Hello, world!"))