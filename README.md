# Bet Or Go iOS 云打包工程

这个工程只包含 iOS 外壳、已经构建的手机界面资源和云编译脚本。无需 Apple 开发者会员或签名证书即可编译供侧载工具重新签名的 IPA；需要云端 macOS 和 Xcode 26 或以上。

## 在 GitHub Actions 编译

在 Actions 中选择 **Build iOS IPA for free sideloading**，点击 **Run workflow**。成功后下载 **BetOrGo-iOS-Unsigned** 产物，解压得到 `.ipa`、SHA256、验证报告和构建日志。公开仓库使用 GitHub 标准 macOS runner 的构建分钟免费；私有仓库需先核对免费额度和消费预算。此工作流只由手动操作启动，产物保留 3 天。

本工程不包含 Apple ID、签名私钥、GitHub 登录凭证、服务器数据库或玩家记录。上传公开仓库会公开这里的 iOS 代码与网页界面资源；需要先由工程拥有者同意。

## 免费安装到 iPhone

1. 在 Windows 电脑安装 [Sideloadly](https://sideloadly.io/)，按其要求准备 Apple 官方版本的 iTunes / iCloud 驱动。
2. 用 USB 连接 iPhone，解锁手机并选择信任这台电脑。
3. 将 `.ipa` 拖入 Sideloadly，选择设备，使用安装者自己的 Apple ID 完成签名安装。Apple ID 密码和验证码只在安装者电脑的登录界面中输入，不发送给游戏作者或写进工程。
4. 按手机提示信任开发者；iOS 16 及以上如有要求，开启设置中的开发者模式。
5. 普通 Apple ID 的签名约 7 天到期。可在 Sideloadly 中配置自动续签；续签时电脑需要开机，手机需能通过 USB 或已配对的同一 Wi-Fi 连接电脑。

IPA 下载到手机文件列表后仍需要签名安装。仅下载文件不能完成 iOS 安装。每位朋友可以使用自己的 Apple ID 安装同一个未签名 IPA；免费账号的设备、App ID 和同时安装数量受 Apple 限制。

## 联机

安装包自带离线人机界面。朋友联机需要共同可访问的 HTTPS 服务；在大厅的“联机地址设置”中填写同一个服务器地址，再用房间码加入。默认服务器沿用现有联机设置；本次打包不会新开服务器。

## 验证边界

云构建会检查 IPA 的 ZIP 完整性、arm64 真机 Mach-O、iPhoneOS 平台、版本、离线资源和 SHA256。成功编译不等于已经完成 iPhone 真机安装、声音或联机验证。

参考：[GitHub Actions 计费](https://docs.github.com/en/billing/concepts/product-billing/github-actions)、[Sideloadly](https://sideloadly.io/)、[Capacitor 环境要求](https://capacitorjs.com/docs/getting-started/environment-setup)。
