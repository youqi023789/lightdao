> Bản dịch máy chưa qua hiệu đính con người; nếu có sai khác, bản gốc tiếng Trung được ưu tiên.
[中文原文 / Chinese original](/whitepaper.md)

# Sách trắng LightDAO V2.4 (Phiên bản trực tiếp Mainnet 2026-09-26)

> Phiên bản này dựa trên bản phác thảo thiết kế V2.0, với "triển khai mạng chính trực tiếp" và "các thay đổi phiên bản" ở phía trước và gắn thêm các tham số trên chuỗi đã được xác minh. Văn bản chính (Chương 1~12) không thay đổi so với thiết kế V2.0; đối với mọi sai lệch so với tình hình thực tế thì áp dụng các ghi chú và phụ lục trước đó của phần này.

## Thay đổi phiên bản (V2.0 → V2.4)
- 2026-11-04 Errata (không thay đổi số phiên bản, vẫn là V2.4): Vault gốc `treasury_multisig` trong phụ lục "Thông số và địa chỉ được xác minh của Mainnet" là 5/7 multisig, mâu thuẫn với 3/5 của văn bản §7.2/§7.3/§8.1 và cũng xung đột với phép đo thực tế trên chuỗi (`{"người ký":{}}` trả về 5 địa chỉ, không có 7 người ký); nó đã được thống nhất là 3/5 theo văn bản và được chỉ ra rằng bản thân ngưỡng này không nằm trong giao diện truy vấn hợp đồng và chỉ có thể được hỗ trợ bởi các bản ghi triển khai. Root khai thác ban đầu được viết trong cùng một phần là "5/7 trình xác minh đa chữ ký" và thử nghiệm thực tế chỉ có thể chứng minh ngưỡng 5 (ngưỡng của 115 sự kiện `submit_root` là tất cả 5 và số lượng tài khoản ký thực tế chính xác là 5). Ủy quyền 7 chỗ là mục tiêu thiết kế và hiện không có bằng chứng nào trên chuỗi. Từ ngữ đã được thay đổi cho phù hợp.

1. **§4.5 Tiết kiệm gas: Đã triển khai và xác minh trên mạng chính**. Giá khí tối thiểu linh hoạt được neo bằng USD và mức phá hủy 50% / trình xác thực 30% / phân bổ kho bạc 20% đã được triển khai vào ngày 24 tháng 9 năm 2026 sau khi đề xuất quản trị (v2-lightfee) được đưa ra ở mức cao 58627, 7 trình xác nhận phối hợp chuyển đổi và mạng thử nghiệm đã được diễn tập từ đầu đến cuối. Đo lường thực tế trên mạng chính: phí không đủ sẽ bị từ chối và phí đầy đủ được phân bổ chính xác theo tỷ lệ 50/30/20.
2. **Làm rõ mệnh giá gốc**: Đặt cược/quản trị/Gas đều là `ulight` (LIGHT, 6 chữ số thập phân, tổng nguồn cung 2,5 tỷ). Lạm phát `cổ phần` không khớp với nguồn gốc đã được đặt lại về 0 (lạm phát bạc hà=0) theo đề xuất quản trị vào ngày 24 tháng 9 năm 2026. Việc phát hành LIGHT hoàn toàn do hợp đồng khai thác_reward thực hiện, loại bỏ việc phát hành kép; cổ phần hiện có là mệnh giá kế thừa sẽ được xử lý (xem Phụ lục C).
3. **§4.7 Chuyển tiếp WebRTC: Đã triển khai**. 8 nút quay vòng (TURN/STUN, chứng chỉ TLS Turn-*.lightdao.net) + Tín hiệu WSS + Chứng chỉ tạm thời REST (HMAC-SHA1); các kênh dữ liệu P2P của máy khách được chuyển tiếp lẫn nhau và các byte chuyển tiếp được tính là đóng góp 40% băng thông; phép đo thực tế từ đầu đến cuối thành công thông qua truyền rơle TURN. NAT đối xứng sử dụng TURN và không thể hạ cấp xuống chế độ xác thực thuần túy (phù hợp với §4.7).
4. **§4.9 Ví thông minh: Trực tuyến**. Đăng nhập không cần mật mã/WebAuthn (khóa dẫn xuất PRF + lưu trữ văn bản mã hóa AES-GCM, văn bản gốc không rơi xuống đất) + Phục hồi xã hội Shamir 3/5; cụm từ ghi nhớ được giữ lại làm tùy chọn dự phòng.
5. **§4.10 Giá Oracle: Nguồn cấp dữ liệu giá đã được chạy**. 7 Trình xác minh cron lần lượt gửi external_median tới oracle_twap (giá tham chiếu hiện tại 50000 = 0,05 USD); TWAP trên chuỗi sẽ được kích hoạt sau khi nhóm thanh khoản LIGHT/USDC được thiết lập. Sau khi nâng cấp v3, lightfee trực tiếp đọc external_median và chuyển đổi khí tối thiểu động.
6. **Quản trị tham số**: Bản nâng cấp v3 sẽ chuyển BurnPct/TreasuryPct/TransferUsd/StaticPrice/OracleContract của lightfee vào paramstore trên chuỗi. Các đề xuất tham số quản trị có thể được điều chỉnh trong thời gian chạy, loại bỏ nhu cầu phối hợp nâng cấp.

## Triển khai Mainnet trực tiếp (26/09/2026)

- Chuỗi `lightdao-mainnet-1`, 7 trình xác nhận (JP/KR/SG/US/HK/FR/UK) đều được TRÁI PHIẾU, không có ai bị bỏ tù; đáp ứng điểm mấu chốt cứng rắn của §4.7 "Người xác minh <7 không được phép TGE"
- Khách hàng https://lightdao.net (PWA): Ví Passkey + khai thác + chuyển tiếp WebRTC + bộ sưu tập, đa ngôn ngữ (tiếng Trung/tiếng Anh/tiếng Tây Ban Nha)
- Vòng khép kín khai thác: Đóng góp của trình duyệt → Hoàn thiện cổng hàng ngày → Merkle root 5 được ký trên chuỗi (ngưỡng 5, có thể được kiểm tra trên chuỗi) → Người khai thác nhận được bằng chứng bằng bằng chứng; root hàng ngày được gửi liên tục
- Quản lý nâng cấp: v2-lightfee (áp dụng @58627), mint zeroing (đã áp dụng), v3-lightfee (được nhất trí thông qua, chiều cao 118055 tự động chuyển đổi)
- Để biết lịch sử nâng cấp/địa chỉ hợp đồng/điểm cuối đầy đủ, vui lòng xem kho `docs/MAINNET_STATUS.md`

---

# LightDAO 白皮书 V2.0

**Phiên bản tối ưu hóa xác minh và hiệu đính toàn văn (máy khách web quốc tế · kiểm toán số · kiểm toán bên thứ ba · phiên bản tối ưu hóa mô hình kinh tế) **

Ngày phát hành: ngày 4 tháng 8 năm 2026

Nguyên tắc cốt lõi: Trình duyệt là nút, mọi người đều có thể tham gia và lợi nhuận được chia sẻ theo quy tắc

Định vị pháp lý: LIGHT và mã thông báo phụ được định vị là điểm đóng góp sinh thái và chứng nhận quyền yêu cầu phân phối thu nhập SPV và không phải là chứng khoán hoặc sản phẩm tài chính; các thuộc tính pháp lý cụ thể phải tuân theo các ý kiến ​​pháp lý hợp lệ ở các khu vực pháp lý có liên quan.

> Tài liệu này là phiên bản được xác minh và tối ưu hóa của toàn bộ nội dung của sách trắng và không cấu thành tư vấn đầu tư, tài liệu phát hành chứng khoán, mô tả sản phẩm tài chính hoặc bất kỳ hình thức cam kết bảo lãnh vốn nào. Vui lòng tham khảo ý kiến ​​các chuyên gia pháp lý, thuế và tài chính trước khi tham gia.

---

## Mục lục

- Tuyên bố trước
- Mở đầu: Câu chuyện của ba người
- Chương 1: Sự thật chúng ta thấy
- Chương 2: Câu trả lời của LightDAO
- Chương 3: Tuân thủ và cách ly pháp lý
- Chương 4: Kiến trúc kỹ thuật
- Chương 5: Mô hình kinh tế token
- Chương 6: Cơ chế quản trị
- Chương 7: Kiểm tra, cân bằng quyền lực và xác định vai trò
- Chương 8: Cơ chế tin cậy và bảo mật
- Chương 9: Hoạt động đầu tư và chiến lược rút lui
- Chương 10: Lộ trình
- Chương 11: Văn hóa cộng đồng và hệ sinh thái phát triển
- Chương 12: Đội ngũ và nhà tư vấn
- Chương 13: Cảnh báo rủi ro và miễn trừ trách nhiệm
- Phụ lục A: Bảng tóm tắt các thông số chính
- Phụ lục B: Đạo hàm và kiểm chứng số
- Phụ lục C: Nhật ký sửa lỗi kiểm tra
- Phụ lục D: Mục lục tra cứu nhanh các thuật ngữ

---

## Tóm tắt điều hành

**LightDAO là gì:** Một tổ chức tự trị phi tập trung cho phép người dân bình thường trên khắp thế giới tham gia vào các khoản đầu tư kinh doanh thực sự và chia sẻ lợi nhuận thông qua trình duyệt. Người dùng không cần mua máy khai thác, có nền tảng kỹ thuật hoặc đáp ứng ngưỡng của các nhà đầu tư đủ điều kiện - chỉ với một trình duyệt và một khoảng thời gian nhỏ, người dùng có thể đóng góp tài nguyên mạng để nhận phần thưởng mã thông báo LIGHT và tham gia vào các quyết định đầu tư thông qua bỏ phiếu quản trị.

**Vấn đề gì đã được giải quyết:** 50% dân số dưới cùng toàn cầu (khoảng 4 tỷ người) chỉ sở hữu 2% tổng tài sản (Phòng thí nghiệm Bất bình đẳng Thế giới, 2026). Tài sản chất lượng cao (vốn cổ phần tư nhân, vốn mạo hiểm) bị loại trừ bởi ngưỡng nhà đầu tư đủ điều kiện (thu nhập hàng năm 200.000 USD/giá trị ròng 1 triệu USD). Mặc dù có câu chuyện về "sự tham gia toàn cầu" trong lĩnh vực tiền điện tử, nhưng phần lớn các mã thông báo cuối cùng sẽ trở về 0 (CoinGecko 2025: 11,56 triệu mã thông báo đã chết) và tỷ lệ tham gia quản trị DAO chỉ khoảng 3-12%.

**Cách giải quyết:** Mô hình động cơ kép - 70% vốn được đầu tư vào tài sản tiêu dùng cứng nhắc ở cấp cộng đồng (động cơ dòng tiền) và 30% được đầu tư vào công nghệ tiên tiến (động cơ tăng trưởng). Các khoản đầu tư được thực hiện thông qua Cayman SPV và lợi nhuận được phân phối theo quy tắc trên chuỗi: 40% cho người nắm giữ mã thông báo phụ, 30% trở lại kho để tái đầu tư, 20% mua lại LIGHT để tiêu hủy và 10% được tích lũy vào quỹ bảo hiểm.

**Dữ liệu cốt lõi:**

| Các chỉ số | Giá trị |
|------|------|
| Tổng lượng ÁNH SÁNG | 2,5 tỷ, sẽ không bao giờ được phát hành |
| Kho đầu tư | 850 triệu (có thể triển khai cơ bản ≈ 100 triệu USD) |
| Sản lượng khai thác | 1 tỷ, giảm một nửa sau mỗi 2 năm |
| Được phát hành vào Ngày kỷ nguyên đầu tiên | ≈684.900 miếng (trung bình 6,51/ngày khi 100.000 thợ mỏ làm việc) |
| Điểm mấu chốt của giảm phát | Ngừng đốt vĩnh viễn khi lưu lượng ≤ 1 tỷ (năm 11-12 kịch bản cơ sở) |
| Ngưỡng quản trị | Đề xuất ≥ 5.000 ÁNH SÁNG; Ủy ban ≥ 50.000 ÁNH SÁNG |
| Ngăn xếp công nghệ | SDK vũ trụ + PoS Tendermint + CosmWasm + PWA |
| Người xác minh | Ban đầu 21 (tối thiểu 10), giới hạn trên 100 |
| Tài trợ ban đầu | Đấu giá Hà Lan 15 triệu USD + Tài trợ chiến lược trước TGE 2,25-3,75 triệu USD |

**Sự khác biệt:** Hiện tại là dự án duy nhất kết hợp "khai thác web không ngưỡng" với "đầu tư thực thể SPV tuân thủ". Khác với Pi Network (không có tiện ích thực tế), Helium (yêu cầu phần cứng trên 200 USD) và DAO truyền thống (quản trị ưu tú ở ngưỡng cao).

**Lộ trình:** Chuẩn bị cho Q4 2026 → Phát triển Q1-Q2 2027 → Kiểm tra kiểm toán Q3 → Q4 TGE trực tuyến → Người dùng hạt giống Q1 2028 → Đầu tư đầu tiên vào Q2-Q3 → Quy mô từ Q4 trở đi.

---

## Tuyên bố trước

**Đây không phải là một đề xuất đầu tư**

"Phần thưởng sinh thái" và "phân phối thu nhập theo thỏa thuận" được mô tả trong sách trắng này là các thỏa thuận khuyến khích được tạo ra bởi cơ chế nội sinh của thỏa thuận và không cấu thành bất kỳ hình thức phát hành chứng khoán, bán sản phẩm tài chính, cam kết bảo lãnh vốn hoặc tư vấn đầu tư nào.

LIGHT và các token phụ không có giá trị nội tại và giá có thể trở về 0. Trước khi tham gia, vui lòng tham khảo ý kiến ​​​​các chuyên gia pháp lý, thuế và tài chính của riêng bạn và chịu hoàn toàn trách nhiệm về việc lưu giữ, khai báo thuế và tham gia khóa riêng.

---

## Mở đầu: Câu chuyện của ba người

Maria làm công việc giao đồ ăn ở Manila, làm việc 12 giờ mỗi ngày và kiếm được khoảng 15.000 peso Philippine (khoảng 270 USD) mỗi tháng. Cô muốn đầu tư vào thương hiệu chuỗi trà sữa nổi tiếng bên cạnh, nhưng bên kia nói với cô: “Mức đầu tư tối thiểu bắt đầu từ 25.000 USD”. Maria không thể kiếm được 25.000 đô la Mỹ.

Kwame lái một dịch vụ gọi xe ở Lagos. Anh lạc quan về con đường trí tuệ nhân tạo và muốn đầu tư vào một công ty công nghệ tài chính nhỏ. Tổ chức này nói với anh ấy: "Số tiền đăng ký tối thiểu là 100.000 USD và thời hạn khóa là 5 năm." Kwame không thể kiếm được 100.000 đô la Mỹ.

Elena là một giáo viên đã nghỉ hưu ở São Paulo với mức lương hưu hàng tháng khoảng 3.000 real Brazil (khoảng 550 USD). Cô nghe nói rằng những đứa trẻ hàng xóm của cô đang kiếm tiền khi làm việc trong các công ty blockchain, nhưng cô không thể đọc được sách trắng cũng như không biết cách mua và cấu hình thiết bị khai thác chuyên nghiệp.

Ba người trong số họ đại diện cho đại đa số người dân bình thường trên toàn thế giới: họ có óc phán đoán và sẵn sàng tham gia, nhưng họ thiếu các kênh tham gia ở ngưỡng thấp, minh bạch và giá cả phải chăng.

LightDAO được thiết kế cho những người này. Với một thiết bị hỗ trợ Internet, một trình duyệt và một khoản tiền nhỏ, bạn có thể tham gia xây dựng hệ sinh thái; thông qua cấu trúc SPV tuân thủ, người dùng cũng có cơ hội tiếp cận gián tiếp việc phân phối dòng tiền của các công ty chất lượng cao và sự phát triển ban đầu của các dự án công nghệ tiên tiến.

---

## Chương 1: Sự thật chúng ta thấy

### 1.1 Phân phối tài sản toàn cầu mất cân bằng

Theo Báo cáo Bất bình đẳng Thế giới năm 2026 (sau đây gọi là “Báo cáo”) của Phòng thí nghiệm Bất bình đẳng Thế giới:

| Dữ liệu | Nguồn |
|------|------|
| Tài sản thuộc sở hữu của 0,001% dân số giàu nhất thế giới (khoảng 60.000 người) gấp khoảng ba lần tổng tài sản của 50% dân số dưới cùng (khoảng 4 tỷ người) | Phòng thí nghiệm Bất bình đẳng Thế giới, 2026 |
| 1% dân số hàng đầu thế giới kiểm soát 23% tổng thu nhập và 38% tổng tài sản | Phòng thí nghiệm Bất bình đẳng Thế giới, 2026 |
| 10% dân số hàng đầu thế giới kiểm soát 53% tổng thu nhập và 75% tổng tài sản | Phòng thí nghiệm Bất bình đẳng Thế giới, 2026 |
| 50% dân số dưới cùng toàn cầu chỉ nhận được 8% tổng thu nhập và 2% tổng tài sản | Phòng thí nghiệm Bất bình đẳng Thế giới, 2026 |

"Báo cáo" chỉ ra: "Bất bình đẳng toàn cầu vẫn ở mức cực đoan trong lịch sử. Bất bình đẳng không chỉ phát sinh từ hoạt động tự nhiên của thị trường mà còn phản ánh các lựa chọn chính sách, cơ cấu thể chế và sự phân bổ không đồng đều quyền lực kinh tế và chính trị."

**Nguồn Lưu ý:** Dữ liệu trên được trích dẫn từ Báo cáo Bất bình đẳng Thế giới năm 2026 của Phòng thí nghiệm Bất bình đẳng Thế giới. Báo cáo được dẫn dắt bởi Lucas Chancel, Ricardo Gómez-Carrera, Rowaida Moshrif và Thomas Piketty (được xác nhận bởi trang web chính thức của wid.world). Trước khi phát hành chính thức, nên đánh dấu thêm các số biểu đồ cụ thể trong báo cáo để giảm thiểu các sai sót có thể xảy ra trong bản dịch thứ cấp.

**Kiểm tra tính nhất quán của dữ liệu:** Các tỷ lệ trên tiếp tục có xu hướng hợp lý theo kết luận của Báo cáo Bất bình đẳng Thế giới năm 2022 (10% hàng đầu sở hữu 76% tổng tài sản, 50% dưới cùng sở hữu 2% tổng tài sản) và độ lệch nằm trong phạm vi có thể chấp nhận được về mặt thống kê.

### 1.2 Người bình thường bị loại khỏi tài sản chất lượng cao

Các khu vực pháp lý lớn trên toàn cầu có ngưỡng nhà đầu tư đủ điều kiện nghiêm ngặt đối với vốn cổ phần tư nhân và vốn mạo hiểm:

**Hoa Kỳ (Quy định D của SEC, Quy tắc 501, 17 CFR §230.501):** Các nhà đầu tư đủ điều kiện (Nhà đầu tư được công nhận) phải đáp ứng một trong các điều kiện sau - thu nhập hàng năm của một cá nhân không dưới 200.000 USD (hoặc tổng thu nhập không dưới 300.000 USD với vợ/chồng) và đã đáp ứng tiêu chuẩn trong hai năm liên tiếp; hoặc giá trị ròng (không bao gồm nơi cư trú chính) không dưới 1.000.000 USD.

**EU (MiFID II, 2014/65/EU, Phụ lục II):** Nhà đầu tư chuyên nghiệp (Nhà đầu tư chuyên nghiệp) phải đáp ứng ít nhất hai trong số các điều kiện sau - danh mục đầu tư công cụ tài chính không dưới 500.000 euro; giữ chức vụ chuyên môn trong ngành tài chính ít nhất một năm; thực hiện các giao dịch quy mô lớn không dưới 10 giao dịch mỗi quý.

**Thực hành Quỹ đầu tư tư nhân toàn cầu:** Số tiền đăng ký tối thiểu cho một quỹ thường nằm trong khoảng từ 250.000 USD đến 1.000.000 USD; các quy định pháp lý thường cấm các hành vi trốn tránh như "chia cổ phần, hạ thấp ngưỡng và giữ lệnh thay mặt cho người khác".

| 资产类型 | 普通人能否参与 | 主要原因 |
|----------|---------------|----------|
| 未上市优质企业股权 | 通常不能 | 合格投资者门槛较高，例如美国要求净资产不低于100万美元或年收入不低于20万美元 |
| 风险投资（早期科技公司） | 通常不能 | 主要面向合格投资者开放，单只基金投资金额通常不低于25万美元 |
| 上市公司股票 | 可以，但早期利润通常已被一级市场参与者获取 | 二级市场定价通常包含未来预期，投资者并不直接参与企业早期利润分配 |

### 1.3 Ba lỗ hổng lớn trong lĩnh vực tiền điện tử

**Lỗi 1: Tỷ lệ thất bại cực cao**

Theo báo cáo thống kê thường niên năm 2025 của CoinGecko, khoảng **11,56 triệu token** sẽ trở về 0 hoặc ngừng giao dịch chỉ riêng vào năm 2025 (bao gồm cả các token đuôi dài trên mỗi chuỗi). Trong số hơn 20 triệu token mà CoinGecko đã theo dõi trong lịch sử, đại đa số đều ở trạng thái "chết" (không có khối lượng giao dịch, không có hoạt động phát triển và giá đã giảm hơn 99% so với mức cao lịch sử).

Đồng thời, tỷ lệ thất bại của thị trường chứng khoán truyền thống thấp hơn nhiều so với tiền điện tử. Theo bài báo của Bessembinder (2018) "Cổ phiếu có tốt hơn tín phiếu kho bạc không?" được công bố trên "Tạp chí Kinh tế Tài chính", một nghiên cứu về tất cả chứng khoán Hoa Kỳ từ năm 1926 đến năm 2016:

| Số liệu | Dữ liệu | Nguồn |
|------|------|------|
| Tỷ lệ cổ phiếu tạo ra tổng tài sản ròng | Chỉ khoảng 4% (1.092 cổ phiếu) | Bessembinder (2018), JFE 129(3):440-475 |
| Lợi nhuận trung bình suốt đời cổ phiếu | Tiêu cực (hoạt động kém hơn tín phiếu kho bạc) | Bessembinder (2018), JFE |
| Khoảng 58% hiệu suất trọn đời của chứng khoán Hoa Kỳ | Tín phiếu kho bạc hoạt động kém hiệu quả so với cùng kỳ | Bessembinder (2018), JFE |
| Số lượng token được đặt lại về 0/ngừng giao dịch vào năm 2025 | ≈11,56 triệu | Báo cáo thường niên CoinGecko 2025 |

**Kết luận so sánh:** Tỷ lệ mất vốn vĩnh viễn trong không gian tiền điện tử cao hơn nhiều so với thị trường chứng khoán truyền thống. Mặc dù khoảng 58% cổ phiếu riêng lẻ trên thị trường chứng khoán Mỹ hoạt động kém hơn trái phiếu kho bạc, các nhà đầu tư vẫn có thể thu được lợi nhuận trung bình của thị trường thông qua các quỹ chỉ số; trong thị trường tiền điện tử, phần lớn các mã thông báo cuối cùng sẽ trở về 0 và thiếu các công cụ đa dạng hóa hiệu quả tương tự như "chỉ mục".

**Thông tin nguồn:** Bessembinder, H. (2018). “Cổ phiếu có tốt hơn tín phiếu kho bạc không?” *Tạp chí Kinh tế Tài chính*, 129(3), 440-475. Đại học bang Arizona. Bài viết này là một tài liệu được trích dẫn nhiều trong lĩnh vực tài chính (trích dẫn >2.000) và dữ liệu bao gồm tất cả các cổ phiếu của Hoa Kỳ trong cơ sở dữ liệu CRSP từ năm 1926 đến năm 2016. Dữ liệu của CoinGecko đến từ Báo cáo thống kê tình trạng tồn tại của token năm 2025 (phát hành vào tháng 1 năm 2026), đã được nhiều phương tiện truyền thông tài chính (Sina Finance, Phemex, RBC Crypto) đưa tin.

**Lỗ hổng 2: Việc khai thác mang tính tập trung cao độ**

Khai thác bitcoin đã cho thấy mức độ tập trung cao:

| Nhóm khai thác | Tỷ lệ tỷ lệ băm |
|------|---------|
| Xưởng đúc Mỹ | Khoảng 30% |
| AntPool | Khoảng 19% |
| ViaBTC | Khoảng 14,5% |
| F2Pool | Khoảng 10% |
| Bể bơi MARA | Khoảng 5% |
| Hai nhóm khai thác hàng đầu kết hợp | Hơn 50% |
| Bốn nhóm khai thác hàng đầu kết hợp | Khoảng 75% |

**Lưu ý nguồn:** Dữ liệu trên được tổng hợp từ báo cáo phân phối hashrate hàng tháng của năm 2025 (CoinGradient 2025.3 "Foundry, Antpool và Viabtc thống trị hoạt động khai thác Bitcoin"; HashrateIndex "10 nhóm khai thác Bitcoin hàng đầu năm 2025"). Các giá trị cụ thể từ các nguồn dữ liệu khác nhau có thể thay đổi đôi chút (thường trong phạm vi ±2%), nhưng kết luận rằng “bốn nhóm khai thác hàng đầu kiểm soát khoảng 75% sức mạnh tính toán” được phản ánh trong nhiều nền tảng giám sát chính thống.

**Lỗ hổng 3: Tỷ lệ tham gia quản trị DAO cực kỳ thấp**

| Dữ liệu | Nguồn |
|------|------|
| Tỷ lệ tham gia bỏ phiếu của hầu hết các DAO chỉ khoảng 3%-12% (trung bình là khoảng 6%) | DeepDAO (2025) Tổng hợp dữ liệu quản trị trên chuỗi; Báo cáo quản trị DAO của phòng họp (2024) |
| Một số ít người nắm giữ tiền tệ kiểm soát phần lớn quyền biểu quyết (tập trung quyền lực quản trị cao) | ACM (2024) "Quản trị DAO: Quyền biểu quyết, sự tham gia và tranh cãi" DOI:10.1145/3777416 |

### 1.4 Thông tin cốt lõi

Tôi có phán quyết nhưng không có vé vào cửa; Tôi có tầm nhìn nhưng không có quyền lên tiếng; Tôi muốn tham gia nhưng bị chặn bởi ngưỡng cao.

---

## Chương 2: Câu trả lời của LightDAO

### 2.1 Định vị cốt lõi

LightDAO là một tổ chức tự chủ đầu tư quốc gia với quản trị theo chuỗi là cốt lõi và SPV tuân thủ là nhà cung cấp dịch vụ thực hiện đầu tư. Thông qua chuỗi công khai được thiết kế dành riêng cho các nút web nhẹ, người dùng toàn cầu có thể tham gia bảo trì mạng, bỏ phiếu quản trị và chia sẻ lợi ích sinh thái theo quy tắc chỉ bằng một trình duyệt.

### 2.2 Model động cơ kép

| Động cơ | Định Hướng Đầu Tư | Mục tiêu | Đặc điểm thu nhập |
|------|---------|------|----------|
| Động cơ Một: Động cơ dòng tiền (Shou) | Tài sản dịch vụ tiêu dùng cứng nhắc cấp cộng đồng | Hình thành dòng tiền liên tục và phân phối lợi nhuận theo quy luật | Theo đuổi sự ổn định tương đối nhưng không hứa hẹn thu nhập cố định |
| Động cơ 2: Động cơ tăng trưởng (tấn công) | Công ty công nghệ tiên tiến | Nhận được sự đánh giá cao về vốn chủ sở hữu và lợi nhuận thoát ra | Tính linh hoạt tiềm năng cao nhưng cũng có thể đối mặt với thua lỗ hoặc thất bại khi rút lui |

**Kỷ luật phân bổ:** Về nguyên tắc, phân bổ 70% nguồn vốn cho các tài sản có dòng tiền ổn định và 30% cho các mục tiêu tăng trưởng cao.

**Con đường tăng trưởng quy mô đầu tư:** Quy mô của một khoản đầu tư tăng trưởng linh hoạt theo giá LIGHT và dung lượng kho tiền - giai đoạn khởi động (LIGHT $0,02- $0,05) phù hợp với tài sản nhỏ cấp cộng đồng là 2,55 triệu USD-6,37 triệu USD; giai đoạn tăng trưởng ($0,05-$0,30) tham gia vào các chuỗi khu vực và các vòng Seed-A trị giá 6,37 triệu USD-38,25 triệu USD (điểm chuẩn Thị trường Trung bình Hạ) PE); ở giai đoạn trưởng thành ($0,30-$1,00), nó đạt mức PE thị trường trung bình từ 38,25 triệu USD đến 127,5 triệu USD; ở giai đoạn quy mô ($1,00+), nó có thể thực hiện các thương vụ mua lại quy mô lớn và đầu tư Trước IPO với số tiền hơn 127,5 triệu USD. Ràng buộc cứng: một giao dịch không được vượt quá 15% số tiền còn lại của quỹ đầu tư (xem Chương 9 để biết chi tiết).

**Nguyên tắc định vị mục tiêu đầu tiên:** Thay vì giả định trước một tên công ty cụ thể, trước tiên hãy thiết lập khung sàng lọc - ưu tiên các tài sản dịch vụ tiêu dùng cứng nhắc cấp cộng đồng, yêu cầu mô hình kinh tế một cửa hàng đã được chứng minh, hồ sơ dòng tiền ổn định (biên EBITDA trong ba năm qua không dưới 10% và biến động giữa các năm không cao hơn 15%) và lộ trình mở rộng khu vực rõ ràng. Mục tiêu cụ thể được xác định bởi các đề xuất của cộng đồng.

### 2.3 Đề xuất giá trị cốt lõi

**Trình duyệt là nút** - Không cần mua máy khai thác hoặc có nền tảng kỹ thuật chuyên nghiệp. Bạn có thể tham gia đóng góp mạng bằng cách truy cập nền tảng web chính thức.

**Mọi người đều có thể tham gia** - Sau khi đạt đến ngưỡng quản trị, những người nắm giữ số lượng nhỏ LIGHT cũng có thể tham gia bỏ phiếu để cùng quyết định phương hướng phân bổ vốn.

**Chia sẻ lợi nhuận theo quy định** - Lợi nhuận hoạt động của các công ty đầu tư và lợi nhuận thu được từ các dự án công nghệ sẽ được phân phối theo quy tắc trên chuỗi và thỏa thuận SPV.

### 2.4 Khẩu hiệu

"Trình duyệt của bạn cũng có thể là lối vào nội dung chất lượng cao."

### 2.5 Phân tích sự khác biệt hóa sản phẩm cạnh tranh

| Kích thước | Mạng Pi | Heli | DAO truyền thống (MakerDAO, v.v.) | LightDAO |
|------|----------|--------|----------------------|----------|
| Phương thức tham gia | Bấm vào ỨNG DỤNG di động | Mua điểm phát sóng phần cứng ($200-$1000) | Mua mã thông báo + hoạt động trên chuỗi | Truy cập trình duyệt, chi phí phần cứng bằng 0 |
| Chi phí đầu vào | Không (nhưng không có tiện ích thiết thực) | Cao (phần cứng + cài đặt) | Trung bình đến cao (cần mua token quản trị) | Zero (chỉ là một trình duyệt) |
| Tổng số token | 100 tỷ | 223 triệu | Khác nhau | 2,5 tỷ |
| Hàm đầu tư thực tế | Không có | Không có (chỉ phủ sóng mạng) | Có (nhưng ngưỡng cực cao) | Có (cấu trúc SPV, mọi người đều có thể tham gia) |
| Nguồn thu nhập | Không rõ ràng | Phí sử dụng mạng | Phí thỏa thuận | Lợi nhuận doanh nghiệp + lợi nhuận thoát ra + Phí gas |
| Cách ly hợp pháp | Không có | Không có | Một số có | Cayman SPV+ZK-KYC |
| Tỷ lệ tham gia quản trị | Cực kỳ thấp (không có quản trị đáng kể) | Thấp | Khoảng 6% | Mục tiêu >15% (bỏ phiếu hai chiều + ưu đãi) |

**Sự khác biệt cốt lõi của LightDAO:** Đây hiện là dự án duy nhất kết hợp "khai thác web không ngưỡng" với "đầu tư thực thể SPV tuân thủ". Người dùng không chỉ đóng góp tài nguyên mạng để nhận phần thưởng mã thông báo mà còn trực tiếp tham gia vào các quyết định đầu tư thực sự của doanh nghiệp thông qua bỏ phiếu quản trị và chia sẻ lợi nhuận hoạt động.

> **[Các thuật ngữ trong chương này]**
> **DAO** (Tổ chức tự trị phi tập trung): Một hình thức tổ chức trong đó các quy tắc quản trị được mã hóa thông qua hợp đồng thông minh và các quyết định tập thể được đưa ra bởi chủ sở hữu mã thông báo. Không có hệ thống phân cấp công ty truyền thống.
> **SPV** (Phương tiện có mục đích đặc biệt): một pháp nhân độc lập (thường được đăng ký tại Quần đảo Cayman) được thành lập cho các giao dịch hoặc đầu tư cụ thể nhằm đạt được sự tách biệt rủi ro - các khoản nợ và trách nhiệm pháp lý của SPV không được chuyển đến chính DAO.
> **DePIN** (Mạng cơ sở hạ tầng vật lý phi tập trung, mạng cơ sở hạ tầng vật lý phi tập trung): Mô hình mạng sử dụng mã thông báo để khuyến khích người dùng đóng góp tài nguyên vật lý (băng thông, lưu trữ, sức mạnh tính toán, vùng phủ sóng không dây, v.v.) để xây dựng cơ sở hạ tầng.
> **PE thị trường trung bình thấp** (vốn cổ phần tư nhân trung cấp hạ nguồn): một phân khúc thị trường của ngành cổ phần tư nhân toàn cầu. Quy mô của một giao dịch thường là từ 10 triệu USD đến 100 triệu USD và EBITDA của công ty mục tiêu là từ 2 triệu USD đến 15 triệu USD.

---

##Chương 3: Tuân thủ và cách ly pháp lý

### 3.1 Lớp cách ly pháp lý SPV

DAO không trực tiếp nắm giữ vốn cổ phần trong bất kỳ doanh nghiệp vật chất nào. Tất cả các khoản đầu tư bên ngoài được thực hiện thông qua các phương tiện chuyên dùng (SPV) được thành lập tại Quần đảo Cayman.

| Điểm thiết kế | Mô tả |
|----------|------|
| Điều lệ SPV | Thống nhất rõ ràng rằng hoạt động của SPV phải tuân thủ nghị quyết có hiệu lực của DAO |
| Định nghĩa pháp lý về mã thông báo phụ | Mã thông báo phụ là "Giấy chứng nhận quyền yêu cầu phân phối thu nhập SPV", chỉ thể hiện tiêu chuẩn phân phối cho dòng tiền trong tương lai |
| Không mang theo quyền cổ đông | Không có quyền quản trị doanh nghiệp, ưu đãi thanh lý hoặc bất kỳ quyền cổ đông nào |
| Giám đốc SPV | được phục vụ bởi bên thứ ba độc lập; DAO có thể thay thế giám đốc bằng cách thông qua nghị quyết hợp lệ |
| Giám sát quỹ | Tài khoản ngân hàng được giám sát bởi các tổ chức lưu ký được cấp phép và việc chuyển tiền phải vượt qua xác minh tuân thủ và đa chữ ký |
| Giải quyết tranh chấp SPV | Điều lệ SPV quy định điều khoản trọng tài (SIAC hoặc ICC) và DAO có thể bắt đầu thủ tục tố tụng trọng tài thông qua nghị quyết quản trị |

### 3.2 Xác minh tùy chọn và bảo vệ quyền riêng tư

**Không cần giấy tờ tùy thân để tham gia vào giao thức. ** Truy cập các trang web, tạo ví, đóng góp tài nguyên, nhận LIGHT, bắt đầu và tham gia bỏ phiếu quản trị - không cần tải tài liệu lên trong toàn bộ quá trình và không có thông tin nhận dạng cá nhân (PII) nào được lưu trữ trên chuỗi.

Chỉ khi người dùng tích cực sử dụng dịch vụ của bên thứ ba được quản lý thì việc xác minh rằng chính dịch vụ đó phải hoạt động theo quy định của pháp luật mới được thực hiện. Việc xác minh này được bên cung cấp dịch vụ thu thập, thực hiện và lưu giữ. LightDAO không thu thập, chuyển hoặc lưu trữ bất kỳ dữ liệu nào:

| Kịch bản | Ai thực hiện xác minh | Người dùng cần làm gì |
|---|---|---|
| Mua/bán thông qua các kênh fiat | Các bên thứ ba được cấp phép (như MoonPay, Ramp Network, Transak) | Hoàn thiện quy trình tuân thủ theo yêu cầu riêng của nhà cung cấp dịch vụ |
| Trao đổi mã thông báo phụ (chứng chỉ cổ phần đầu tư) | Tùy theo yêu cầu của sản phẩm cụ thể và nhà cung cấp dịch vụ | Bạn chỉ có thể khai thác và quản trị mà không cần bất kỳ xác minh nào |
| Rút về thẻ ngân hàng/thanh toán nội địa | Nhà cung cấp dịch vụ rút tiền và thanh toán | Hoàn tất quy trình tuân thủ theo yêu cầu của nhà cung cấp dịch vụ |

Nguyên tắc cốt lõi: **Không xác minh theo mặc định; việc xác minh chỉ xảy ra tại thời điểm người dùng chủ động tham gia dịch vụ được quản lý và do nhà cung cấp dịch vụ chịu. **Không ai sẽ mất quyền khai thác, nắm giữ, chuyển nhượng hoặc bỏ phiếu do "không xác minh".

> Công nghệ dành riêng: Nếu một loại tài sản nhất định yêu cầu ngưỡng đủ tiêu chuẩn trong tương lai, người dùng sẽ giữ thông tin xác thực của riêng họ dưới dạng bằng chứng không có kiến ​​thức (ZK) và chuỗi sẽ chỉ xác minh "liệu nó có được đáp ứng hay không" mà không có bất kỳ thông tin nhận dạng nào - đây là một phần của lộ trình và không phải là yêu cầu hiện tại.

### 3.3 Tuyên bố trách nhiệm nộp thuế

Thỏa thuận không cung cấp dịch vụ khai thuế và nghĩa vụ thuế đối với tất cả các phần thưởng sinh thái và thu nhập liên quan đều do người dùng tự chịu. Người dùng nên tuân thủ luật pháp và quy định có liên quan của địa điểm cư trú thuế của họ.

### 3.4 Quyền truy cập của người dùng: dành cho tất cả mọi người

**Không có ngưỡng đăng ký và tham gia**: Không cần email, số điện thoại di động, tài khoản mạng xã hội hoặc bằng chứng nhận dạng; một thiết bị có thể mở một trang web là tất cả những gì bạn cần. LightDAO ** không tích cực hạn chế sự tham gia của người dùng ở bất kỳ quốc gia hoặc khu vực nào và cũng không triển khai tính năng khoanh vùng địa lý. **

Các hạn chế bên ngoài duy nhất đến từ các dịch vụ của bên thứ ba: nếu luật pháp của một nơi nhất định có các yêu cầu khác đối với các dịch vụ cụ thể (chẳng hạn như gửi và rút tiền pháp định), các dịch vụ đó sẽ được thực hiện bởi các tổ chức được cấp phép tại địa phương theo luật của họ và sẽ không ảnh hưởng đến việc sử dụng các chức năng trên chuỗi của bất kỳ ai (khai thác, nắm giữ, chuyển nhượng, bỏ phiếu, đề xuất).

Nếu một khu vực tài phán nhất định ban hành các quy định cấm rõ ràng trong tương lai, trình tự phản hồi của giao thức là:

1. Trước tiên, hãy đảm bảo rằng quyền xử lý tài sản của người dùng hiện tại không bị ảnh hưởng - tài sản trên chuỗi không thể bị đóng băng và bất kỳ ai cũng có thể chuyển LIGHT và mã thông báo phụ của họ bất kỳ lúc nào;
2. Vẫn có thể truy cập được thông qua nhiều cổng giao diện người dùng (bao gồm cả máy nhân bản IPFS và máy nhân bản cộng đồng);
3. Bước cuối cùng là điều chỉnh phạm vi sẵn có của **dịch vụ bên thứ ba** trong phạm vi thực thi pháp luật.

Nói một cách dễ hiểu: các hạn chế về *** chỉ có thể áp dụng cho các dịch vụ chứ không phải cho con người. **

### 3.5 Gửi và rút tiền hợp pháp và các kênh xuyên chuỗi

**Kênh tiền tệ Fiat (tổng hợp dịch vụ của bên thứ ba):** Bản thân giao thức không vận hành dịch vụ gửi và rút tiền hợp pháp, nhưng nền tảng web tích hợp các kênh bên thứ ba tuân thủ (MoonPay, Ramp Network, Transak, v.v.), bao gồm các thị trường lớn ở Bắc Mỹ, Châu Âu, Đông Nam Á và Châu Mỹ Latinh; tổng hợp thị trường P2P địa phương bao gồm Châu Phi và Nam Á; rút tiền hỗ trợ các phương thức thanh toán địa phương như GCash, M-Pesa, Pix và GrabPay.

**Cầu nối chuỗi chéo và các kênh mua lại LIGHT:** Các giao dịch AMM tích hợp trong chuỗi LightDAO sau TGE; khả năng tương tác với hệ sinh thái Cosmos thông qua IBC; lập kế hoạch cho wLIGHT (Ethereum/Solana) từ tháng thứ 6; đăng ký niêm yết trên CEX từ tháng thứ 6 tùy theo mức độ tuân thủ. Cầu nối chuỗi chéo được vận hành bởi một bên thứ ba độc lập và cần phải có báo cáo kiểm toán độc lập trước khi cầu nối trực tuyến.

### 3.6 Tuyên bố tuân thủ cơ chế lời mời (Phân tích chống MLM)

Khuyến khích lời mời của LightDAO là **chia sẻ một lớp** (chỉ những người mời trực tiếp mới nhận được một tỷ lệ cố định trong phần thưởng khai thác của người được mời) và không có các tính năng cốt lõi của tiếp thị đa cấp (MLM): không có hoa hồng đệ quy đa cấp; doanh thu đến từ việc phát hành các mã thông báo đặt trước trong giao thức chứ không phải tiền gốc của người mới; không có chi phí và không có phí tham gia khai thác. Cấu trúc này gần hơn với "phần thưởng khuyến nghị của người đóng góp cho dự án nguồn mở". Trước khi hoạt động chính thức, một luật sư được cấp phép ở thị trường mục tiêu sẽ được thuê để đưa ra ý kiến ​​tuân thủ đặc biệt.

> **[Các thuật ngữ trong chương này]**
> **KYC** (Biết khách hàng, Biết khách hàng của bạn): Một quy trình tuân thủ dành cho các tổ chức tài chính để xác minh danh tính người dùng, thường yêu cầu gửi giấy tờ nhận dạng, bằng chứng địa chỉ, v.v.
> **ZK-KYC** (Zero-Knowledge KYC, zero-know KYC): Người dùng không cần tiết lộ thông tin cá nhân cụ thể cho thỏa thuận và chỉ sử dụng mật mã để chứng minh phương pháp xác minh tuân thủ "Tôi đáp ứng một số điều kiện nhất định" (chẳng hạn như tuổi ≥ 18 tuổi, quốc tịch không bị trừng phạt). Không có dữ liệu tài liệu gốc nào được lưu trữ trên chuỗi.
> **PII** (Thông tin nhận dạng cá nhân, Thông tin nhận dạng cá nhân): Dữ liệu có thể nhận dạng một thể nhân cụ thể một cách riêng lẻ hoặc kết hợp, chẳng hạn như tên, số ID, địa chỉ, đặc điểm sinh trắc học, v.v.
> **Reg D / Reg S** (Quy định D/Quy định S của Đạo luật Chứng khoán Hoa Kỳ): Reg D cho phép phát hành riêng lẻ cho "các nhà đầu tư đủ điều kiện" tại Hoa Kỳ mà không cần đăng ký công khai (tiêu chuẩn định nghĩa Quy tắc 501); Reg S cho phép bán chứng khoán cho những người bên ngoài Hoa Kỳ mà không cần đáp ứng các yêu cầu đăng ký của Hoa Kỳ.
> **MiFID II** (Chỉ thị II về Công cụ Tài chính của Thị trường EU, 2014/65/EU): Khung quy định tài chính của EU, Phụ lục II của nó xác định các tiêu chí nhận dạng dành cho "nhà đầu tư chuyên nghiệp" (danh mục công cụ tài chính trị giá €500K, 1 năm kinh nghiệm trong ngành tài chính, 10 giao dịch quy mô lớn mỗi quý, đáp ứng yêu cầu thứ hai).
> **MLM** (Tiếp thị đa cấp, tiếp thị đa cấp): mô hình kinh doanh thông qua hoa hồng đệ quy đa cấp (phát triển tuyến dưới, phát triển tuyến dưới và hoa hồng tuyến trên theo từng lớp). Về cơ bản, nó khác với phần thưởng đề xuất một lớp - LightDAO chỉ có một lớp (A mời B, A nhận phần từ B; B mời C, A không nhận được bất kỳ phần nào từ C).
> **IBC** (Giao tiếp liên chuỗi khối, giao thức liên lạc chuỗi chéo): tiêu chuẩn chuỗi chéo gốc của hệ sinh thái Cosmos, cho phép chuyển tài sản và tin nhắn một cách an toàn giữa các chuỗi khối khác nhau mà không cần đến trung gian tập trung.

---

## Chương 4: Kiến trúc kỹ thuật

### 4.1 Chuỗi công khai là gì?

Chuỗi công khai của LightDAO có thể được hiểu là "sổ tài khoản công khai với các quy tắc minh bạch và không thể bị giả mạo theo ý muốn": các quy tắc quản trị được viết thành mã và hồ sơ biểu quyết, dòng vốn và phân phối lợi nhuận của bất kỳ ai đều có thể được truy vấn và xác minh trên chuỗi.

### 4.2 Thông số kỹ thuật và trình diễn lựa chọn

| Mặt hàng kỹ thuật | Lựa chọn | Cơ sở lựa chọn |
|--------|------|---------|
| Khung cơ bản | SDK vũ trụ | Kiến trúc mô-đun, xác minh nhiều chuỗi sản xuất |
| Cơ chế đồng thuận | PoS bạc hà | Sự chắc chắn ngay lập tức; việc tạo khối mất 1,5-2 giây; Khả năng chịu lỗi BFT 1/3 ác |
| Hợp đồng thông minh | Vũ trụWasm | WebAssembly + Rust, an toàn bộ nhớ khi biên dịch |
| Khả năng chuỗi chéo | Giao thức IBC | Tiêu chuẩn chuỗi chéo gốc của Cosmos |
| Tương tác mặt trước | Ứng dụng web lũy tiến (PWA) | Chạy trình duyệt, thích ứng với máy tính để bàn/thiết bị di động, không cần cài đặt |

### 4.3 Cơ chế khai thác nút nhẹ và mô hình khuyến khích

#### 4.3.1 Phương pháp khai thác

Người dùng truy cập nền tảng web chính thức thông qua trình duyệt, tạo ví và nhấp vào "Bắt đầu khai thác". Trong quá trình khai thác, người dùng đóng góp băng thông mạng (chuyển tiếp và xác minh dữ liệu) và tài nguyên máy tính cục bộ (xác minh tiêu đề khối nhẹ) thông qua trình duyệt và không dựa vào sức mạnh tính toán năng lượng cao.

**Triển khai công nghệ phía web:** Chuyển tiếp P2P kênh dữ liệu WebRTC; Xác minh tiêu đề khối nền Web Worker; Bộ đệm và nhịp tim ngoại tuyến của Service Worker; WebSocket kết nối dài.

**Điều chỉnh trình duyệt di động:** Áp dụng hệ thống phiên hợp lệ tích lũy (4 giờ một ngày = 100% điểm); không bị trừ điểm khi kết nối lại trong vòng 5 phút sau khi ngắt kết nối; Người dùng đã cài đặt PWA sẽ nhận thêm 10% tiền thưởng thời gian trực tuyến; cơ chế ủy quyền trực tuyến (70% cho đại biểu/30% cho nút chuyển tiếp).

#### 4.3.2—4.3.3 Cơ chế khuyến khích và mô hình ba động cơ

Nó áp dụng mô hình ba động cơ là "Bằng chứng đóng góp PoC + khuyến khích phân hạch lời mời + khuyến khích tiền thưởng hành vi".

#### 4.3.4 Kích thước và trọng lượng đóng góp

| Thứ nguyên đóng góp | Cân nặng | Phương pháp đo |
|----------|------|---------|
| Đóng góp chuyển tiếp băng thông | 40% | Tỷ lệ lưu lượng chuyển tiếp tải lên trên khối lượng dữ liệu xác minh |
| Thời lượng phiên hiệu quả | 30% | Số buổi hiệu quả tích lũy hàng ngày (4 giờ = 100%) |
| Chặn đóng góp xác minh | 20% | Số lượng và độ chính xác của các tiêu đề khối được xác minh hiệu quả |
| Ổn định mạng | 10% | Độ trễ kết nối, tốc độ mất gói, thời gian phản hồi |

#### 4.3.5 Công thức tính thưởng

**Phần thưởng khai thác hàng ngày = Phần thưởng cơ bản × Điểm trọng lượng đóng góp × (1 + Tiền thưởng cho lời mời) × (1 + Tiền thưởng hành vi)**

- BaseReward = Tổng số tiền được toàn mạng phát hành trong ngày ÷ Tổng số người khai thác hoạt động trong ngày
- Phần thưởng cho lời mời = số lượng người được mời hiệu quả × 1% (giới hạn trên 20%)
- Phần thưởng hành vi = 5% tham gia bỏ phiếu + 5% đóng góp nội dung + 5% hoạt động cộng đồng + 5% chất lượng xác minh nút (giới hạn trên 20%)
- Hệ số thưởng đầy đủ = (1+20%) × (1+20%) = 1,44 lần

#### 4.3.6 Mời khuyến khích phân hạch

| Cấp độ | Số lượng lời mời hợp lệ | Tỷ lệ chia sẻ lời mời | Phần thưởng bổ sung một lần | Thưởng trọng lượng quản trị |
|------|-------------|-------------|--------------|-------------|
| Thợ mỏ | 0 người | — | Phần thưởng khai thác cơ bản | Không có |
| Nhà truyền giáo | Không ít hơn 3 người | 10% | 100 ÁNH SÁNG | Không có |
| Đại sứ | Không dưới 10 người | 15% | 500 LIGHT + huy hiệu trên dây chuyền | Tỷ trọng biểu quyết +5% |
| Đối tác | Không dưới 50 người | 20% | 2.500 LIGHT + huy hiệu trên dây chuyền | Tỷ trọng biểu quyết +10% |

Phần thưởng trọng lượng quản trị và phần thưởng danh tiếng (lên tới +30%) được xếp chồng độc lập, với tổng giới hạn trên là +40%. Phần thưởng cho lời mời đạt đến đỉnh điểm khi có 20 người (20×1%=20%).

#### 4.3.7 Cơ chế chống gian lận

Phát hiện tính toàn vẹn của môi trường trình duyệt (vân tay Canvas/WebGL/WebRTC), phát hiện độ sâu gói, phân cụm IP và phân tích mẫu hành vi, dấu vân tay hành vi đa chiều (quỹ đạo chuột/nhịp bàn phím/hành vi cuộn), xác minh tính xác thực của địa chỉ lời mời. Chi phí tấn công chống Sybil: 50.000-200.000 USD để tạo 10.000 dấu vân tay độc lập; mục tiêu tỷ lệ phát hiện >90-95%.

### 4.4 Ma trận hàm mã thông báo LIGHT

Nhiên liệu mạng (phí Gas), quyền quản trị (bỏ phiếu/đề xuất/chiến dịch), ràng buộc cam kết (ký quỹ/chiến dịch/xác minh), trao đổi đầu tư (mã thông báo phụ), khuyến khích sinh thái (khai thác/lời mời/hành vi), mở rộng trong tương lai (dApp/NFT/chuỗi chéo).

### 4.5 Cơ chế phí gas và phí giao dịch

**Nguyên tắc thiết kế:** Phí gas được cố định bằng USD tương đương và lượng LIGHT thực tế được sạc sẽ được nhà tiên tri trên chuỗi tự động chuyển đổi sau mỗi 24 giờ (Phần 4.10). Điều này đảm bảo rằng bất kể giá LIGHT tăng hay giảm, chi phí thanh toán thực tế của người dùng (bằng đô la Mỹ) vẫn ổn định, tránh được vấn đề "giá tiền tệ tăng 100 lần → phí chuyển khoản trở thành 10 USD" hoặc "giá tiền tệ giảm 90% → đổi vé không tốn phí".

**Mục tiêu phí gas cố định bằng USD:**

| Loại giao dịch | mục tiêu tương đương USD | Bộ sưu tập thực sự khi LIGHT=$0,05 | Bộ sưu tập thực sự khi LIGHT=$0,50 | Ý định thiết kế |
|----------|-------------|-------------------|-------------------|----------|
| Chuyển khoản thông thường | 0,001 USD | 0,02 ÁNH SÁNG | 0,002 ÁNH SÁNG | Ngưỡng cực thấp để đảm bảo người dùng với số tiền nhỏ có thể chuyển tiền thoải mái |
| Biểu quyết quản trị | 0,005 USD | 0,10 ÁNH SÁNG | 0,01 ÁNH SÁNG | Cao hơn một chút so với chuyển khoản để tránh việc bỏ phiếu không tốn kém |
| Gửi đề xuất | 0,10 USD | ÁNH SÁNG 2.0 | 0,2 ÁNH SÁNG | Hợp tác với hệ thống tiền gửi để tăng mức độ nghiêm túc của đề xuất |
| Trao đổi mã thông báo phụ | 0,50 USD | ÁNH SÁNG 10.0 | ÁNH SÁNG 1.0 | Phí cao hơn, phù hợp với mức độ nghiêm túc của hoạt động quy mô lớn |
| Báo cáo nhịp tim khai thác | $0 (miễn phí) | 0 | 0 | Không tính phí Gas cho các khoản đóng góp khai thác, đảm bảo việc tham gia không tốn phí |

**Quy tắc chuyển đổi động:**

- 实际Gas费（LIGHT）= USD目标 ÷ 预言机24h TWAP价格
- 每24小时（UTC 00:00区块）由oracle_twap合约自动更新换算比率
- 设置下限：任何交易类型的Gas费不低于0.001 LIGHT（防止价格为零时Gas归零）
- 设置上限：任何交易类型的Gas费不高于100 LIGHT（防止价格极低时Gas过高阻碍使用）
- USD目标值本身可通过微型提案（$100保证金）由治理调整

**Quy tắc phân bổ phí gas:**

| Điểm đến | Tỷ lệ | Chức năng |
|------|------|------|
| Bị phá hủy vĩnh viễn | 50% | Tiếp tục giảm phát, giảm nguồn cung lưu thông |
| Phần thưởng xác thực | 30% | Khuyến khích người xác thực duy trì an ninh mạng và tạo khối |
| Kho bạc sinh thái | 20% | Nguồn tài trợ bổ sung cho nhà phát triển và quỹ hoạt động cộng đồng |

**Ước tính giảm phát phí gas:** Giả sử trung bình có 100.000 giao dịch hoạt động hàng ngày và phí gas trung bình là 0,005 USD (chủ yếu là bỏ phiếu và chuyển khoản), số USD tương đương bị tiêu hủy mỗi ngày = 100.000 × 0,005 USD × 50% = 250 USD/ngày. Khi LIGHT=0,05 USD, nó tương đương với 5.000 LIGHT/ngày≈1,825 triệu/năm; khi LIGHT=$0,50, nó tương đương với 500 LIGHT/ngày≈182.500/năm. Số lượng LIGHT với giảm phát phí gas giảm khi giá tăng (số tiền tương đương với USD không đổi), nhưng sự hỗ trợ của nó đối với giá được phản ánh bằng việc "liên tục mua số tiền tương đương" - mỗi giao dịch sẽ hủy mã thông báo theo tỷ giá USD cố định.

### 4.6 Hệ thống xác minh

| Kích thước | Trình xác nhận | Các nút nhẹ (công cụ khai thác trình duyệt) |
|------|--------|-------------------|
| Trách nhiệm | Tạo khối, đồng thuận, nút đầy đủ | Xác minh tiêu đề khối, chuyển tiếp dữ liệu |
| Đặt cược | Tối thiểu 500.000 ÁNH SÁNG | Không có |
| Thu nhập | Phí gas 30% + nhóm phát hành hàng ngày 5% | Phần thưởng khai thác PoC (nhóm phát hành hàng ngày 95%) |
| Số lượng | Ban đầu 21, giới hạn trên 100 | Không có giới hạn trên |
| Chém | Phạt 5% khi ký hai lần + cấm 180 ngày | Không có |

**Bắt đầu theo từng giai đoạn (Dung sai lỗi BFT: N ≥3f+1):**

| Giai đoạn | Số lượng người xác nhận | Khả năng chịu lỗi f | Điều kiện dừng xích | Trải nghiệm người dùng |
|------|----------|-------|----------|----------|
| Testnet (3 tháng trước TGE) | 7 | 2 | 3 ngoại tuyến cùng lúc | Thử nghiệm nội bộ có thể chịu được sự gián đoạn ngắn |
| Mạng chính TGE | Tối thiểu 10, mục tiêu 21 | 3-6 | 4-7 ngoại tuyến cùng lúc | Thỉnh thoảng bị gián đoạn (<1 lần mỗi quý) để suôn sẻ |
| Bắt đầu bầu cử từ tháng 7 | 21-100 | 6-33 | 7-34 ngoại tuyến cùng lúc | Người dùng không biết |

**Điểm mấu chốt: TGE sẽ không được thực thi khi có <7 trình xác thực. ** Nhỏ hơn 7 có nghĩa là f ≤ 1. Bất kỳ lỗi một điểm nào cũng sẽ khiến toàn bộ chuỗi ngừng hoạt động, tương đương với "sản phẩm không có sẵn" đối với người dùng không rành về kỹ thuật.

### 4.7 Lớp cơ sở hạ tầng mạng

Các nút trình xác thực mang các cổng truy cập WebSocket theo cách phân tán (mỗi trình xác thực có giới hạn trên là 50.000 kết nối); Tín hiệu P2P được cung cấp bởi trình xác thực + nút chuyển tiếp cộng đồng; tập hợp Merkle nhịp tim chỉ gửi hàm băm gốc trên mỗi khối (O(1) chi phí trên chuỗi); giao diện người dùng được phân phối thông qua IPFS+CDN.

Mạng P2P: Khung WebRTC ICE (ưu tiên STUN/dự phòng TURN); khoảng 70-80% người dùng có thể kết nối trực tiếp, 20-30% người dùng NAT đối xứng chuyển tiếp TURN; khi P2P không thành công, nó sẽ bị hạ cấp xuống "chế độ xác thực thuần túy".

Thông số hiệu suất: TPS lý thuyết 1.000-3.000; kích thước khối 2MB (có thể điều chỉnh quản trị); đồng bộ hóa nút nhẹ <30 giây; tổng hợp nhịp tim triệu nút Merkle <500ms.

### 4.8 Cơ chế xác minh bằng chứng đóng góp

Kiến trúc xác minh ba tầng: (1) Thử thách lấy mẫu chéo ngẫu nhiên của người xác minh (5% nút cứ sau 10 phút, thời gian phản hồi 30 giây); (2) Xác minh lẫn nhau ngang hàng P2P (8-16 đồng nghiệp ghi lại khối lượng trao đổi dữ liệu một cách độc lập, lấy giá trị trung bình); (3) Tổng hợp Merkle trên chuỗi (mỗi khối gửi điểm đóng góp Root, người dùng có thể tự kiểm tra thông qua Merkle Proof). Không thể khiêu chiến 3 lần liên tiếp → điểm trong ngày sẽ bị đặt lại về 0; tổng cộng 5 lần trong vòng 7 ngày → đánh giá chống gian lận sẽ được kích hoạt.

### 4.9 Quản lý ví và chìa khóa

Kiến trúc ba tầng: (1) Ví thông minh nhúng (Passkey/WebAuthn, không yêu cầu cụm từ ghi nhớ, nhắm mục tiêu trên 80% người dùng); (2) Ví phục hồi xã hội (3-5 người khôi phục, phân mảnh Shamir, xác nhận đa số 2/3); (3) Ví tự lưu trữ (cụm từ ghi nhớ BIP-39 + ví phần cứng tương thích). Phí gas cho 100 giao dịch đầu tiên của người dùng mới sẽ được thanh toán bởi quỹ sinh thái (mô hình Paymaster).

### 4.10 Giá Oracle

TWAP trên chuỗi (giá trung bình có trọng số trong thời gian 30 ngày của nhóm LIGHT/USDC) là nguồn giá chính; Tổng hợp DEX/CEX bên ngoài 3+ được bổ sung (trình xác thực gửi luân phiên, lấy trung vị); độ lệch >±15% kích hoạt cờ ngoại lệ; độ lệch khối đơn >5% không được tính vào TWAP (chống thao túng khoản vay nhanh); dự phòng thành TWAP thuần túy trên chuỗi khi tất cả các oracle bên ngoài đều thất bại.

### 4.11 Kiến trúc mô-đun hợp đồng thông minh

10 hợp đồng cốt lõi: light_token, mining_reward, quản trị, kho bạc_multisig, subtoken_factory, oracle_twap, anti_fraud, validator_registry, vesting, Insurance_fund. Hợp đồng cốt lõi phải hoàn tất xác minh chính thức trước TGE.

### 4.12 Nâng cấp giao thức và quản trị chuỗi

Nâng cấp cấp 4: Điều chỉnh tham số L1 (bỏ phiếu quản trị 24-72h) → Di chuyển hợp đồng L2 (đề xuất chính + kiểm toán + độ trễ 72 giờ) → Thay đổi đồng thuận L3 (66% được thông qua + 2/3 tín hiệu xác thực + thời gian bảo vệ fork 7 ngày) → Sửa chữa khẩn cấp L4 (đình chỉ ủy ban bóng tối + sửa lỗi nóng đa chữ ký + phê chuẩn 72 giờ).

> **[Các thuật ngữ trong chương này]**
> **Cosmos SDK**: Khung phát triển chuỗi khối mô-đun cho phép các nhà phát triển tập hợp các chuỗi công khai tùy chỉnh giống như các khối xây dựng. Một số chuỗi sản xuất (như Cosmos Hub và Osmosis) đã xác minh được sự trưởng thành của nó.
> **Tendermint PoS** (Bằng chứng cổ phần, Bằng chứng cổ phần): Một cơ chế đồng thuận trong đó người xác thực có quyền tạo khối bằng cách cam kết mã thông báo (thay vì cạnh tranh về sức mạnh tính toán). Cung cấp "tính hữu hạn ngay lập tức" - một khi một khối được cam kết, nó không thể được khôi phục.
> **BFT** (Byzantine Fault Tolerance, Byzantine Fault Tolerance): Một cơ chế trong hệ thống phân tán có thể chấp nhận một số nút làm điều xấu hoặc gặp trục trặc mà vẫn đạt được sự đồng thuận chính xác. Tendermint BFT có thể chấp nhận không quá 1/3 số người xác thực hành động xấu xa hoặc ngoại tuyến cùng một lúc.
> **CosmWasm**: Công cụ hợp đồng thông minh của hệ sinh thái Cosmos, dựa trên công nghệ WebAssembly, hỗ trợ sử dụng ngôn ngữ Rust để viết hợp đồng và có các tính năng an toàn bộ nhớ trong thời gian biên dịch (ngăn chặn các lỗ hổng phổ biến như tràn bộ đệm).
> **PWA** (Ứng dụng web lũy tiến, Ứng dụng web lũy tiến): Công nghệ web chạy trên trình duyệt nhưng có trải nghiệm ứng dụng giống như ứng dụng gốc. Nó hỗ trợ bộ nhớ đệm ngoại tuyến, thông báo đẩy và thêm vào màn hình chính mà không cần tải xuống và cài đặt thông qua cửa hàng ứng dụng.
> **WebRTC/WebSocket**: Hai công nghệ giao tiếp thời gian thực của trình duyệt. WebRTC được sử dụng để chuyển tiếp dữ liệu P2P (truyền trực tiếp giữa các nút); WebSocket được sử dụng để duy trì kết nối lâu dài giữa máy khách và người xác minh (thông báo nhịp tim, phần thưởng).
> **PoC** (Bằng chứng đóng góp): Cơ chế khuyến khích được LightDAO áp dụng sẽ trao phần thưởng bằng cách xác minh tài nguyên mạng (chuyển tiếp băng thông, xác minh khối, thời gian trực tuyến) thực sự do người dùng đóng góp, thay vì dựa vào cạnh tranh sức mạnh tính toán hoặc cam kết vốn.
> **Cây Merkle** (Cây Merkle): Cấu trúc dữ liệu cây băm cho phép xác minh hiệu quả tính toàn vẹn của một mục cụ thể trong một lượng lớn dữ liệu. Sách trắng này được sử dụng để tổng hợp hàng triệu nhịp tim của nút ánh sáng thành một hàm băm Root duy nhất và tải nó lên chi phí lưu trữ chuỗi (O(1)).
> **Phí gas**: Phí xử lý cần thiết để thực hiện các giao dịch hoặc hoạt động hợp đồng trên blockchain, được sử dụng để bù đắp cho người xác minh về tài nguyên tính toán và lưu trữ. Phí Gas của LightDAO được cố định bằng USD tương đương và được nhà tiên tri tự động chuyển đổi thành lượng LIGHT sau mỗi 24 giờ.
> **Chém** (hình phạt): Cơ chế xử phạt trong đó người xác minh buộc phải khấu trừ một phần số token đã cầm cố do hành vi xấu (chẳng hạn như ký hai lần) hoặc ngoại tuyến trong thời gian dài. Đó là sự đảm bảo kinh tế cho tính bảo mật của mạng PoS.
> **Oracle** (Oracle): Một thành phần cơ sở hạ tầng truyền dữ liệu ngoài chuỗi một cách an toàn (chẳng hạn như giá thị trường, thời tiết, tỷ số thể thao) vào các hợp đồng thông minh trên chuỗi. LightDAO sử dụng kiến ​​trúc oracle lai của tập hợp đa nguồn TWAP + trên chuỗi.
> **TWAP** (Giá trung bình tính theo thời gian): Giá của mỗi khối trong một khoảng thời gian được tính bằng nhau theo thời gian để giảm tác động thao túng của các giao dịch số lượng lớn tức thời đối với tham chiếu giá.
> **AMM** (Nhà tạo lập thị trường tự động): Một giao thức giao dịch phi tập trung thực hiện trao đổi mã thông báo thông qua nhóm thanh khoản (chứ không phải sổ đặt hàng). Giá được xác định tự động theo tỷ lệ tài sản trong nhóm theo công thức.
> **DEX / CEX**: DEX (Sàn giao dịch phi tập trung, sàn giao dịch phi tập trung) không cần lưu trữ tài sản của người dùng và giao dịch ngang hàng thông qua hợp đồng thông minh; CEX (Centralized Exchange, sàn giao dịch tập trung) yêu cầu nhà điều hành lưu giữ tài sản và khớp các giao dịch.
> **IPFS** (Hệ thống tệp liên hành tinh, Hệ thống tệp liên hành tinh): Giao thức phân phối và lưu trữ tệp phi tập trung, được sử dụng trong sách trắng này để lưu trữ các ứng dụng ngoại vi chống kiểm duyệt (ngay cả khi tên miền bị chặn, người dùng vẫn có thể truy cập nền tảng thông qua IPFS).

---

## Chương 5: Mô hình kinh tế token

### 5.1 Tổng thể cơ sở thiết kế

**Tổng nguồn cung LIGHT: 2,5 tỷ (2.500.000.000) và sẽ không bao giờ được phát hành thêm. **

| Dự án điểm chuẩn | Tổng số tiền | Phương thức tham gia | So sánh với LightDAO |
|----------|------|----------|-------------------|
| Bitcoin | 21 triệu | Máy khai thác PoW | Tường thuật tham khảo, ngưỡng cao xa |
| Khí Heli (HNT) | 223 triệu | Điểm truy cập phần cứng $200+ | Điểm chuẩn DePIN, quy mô giới hạn phần cứng |
| Filecoin (FIL) | 2 tỷ | Phần cứng lưu trữ | Gần nhất về mức độ, cả hai đều là "đóng góp tài nguyên để đổi lấy token" |
| Kaspa (KAS) | 28,7 tỷ | Card đồ họa PoW | Quá lớn, giảm đều có giá trị tham chiếu |
| Mạng Pi | 100 tỷ | Số nhấp chuột trên thiết bị di động | Tài liệu giảng dạy tiêu cực: Tổng số tiền quá lớn → nhận thức về giá trị cực kỳ thấp |

**Lý do cốt lõi để chọn 2,5 tỷ xu:**

1. **Năng lực đầu tư (hạn chế chính):** 850 triệu xu trong kho × giá cơ bản 0,15 USD × tỷ lệ sử dụng 75% = **95,63 triệu USD ≈ 100 triệu USD** vốn có thể triển khai, đạt đến ngưỡng đáng tin cậy tối thiểu của PE Thị trường Trung bình Thấp. Cơ sở học thuật: Cong, Li & Wang (2021) "Tokenomics: Áp dụng và định giá linh hoạt" (*Đánh giá về nghiên cứu tài chính* 34(3):1105-1155, NBER w27222) chứng minh rằng tiện ích nền tảng (lợi tức đầu tư → mua lại → hỗ trợ giá) là động lực cơ bản của giá trị mã thông báo, chứ không phải độ rộng phân phối.
2. **Hướng dẫn mạng:** 1 tỷ xu được khai thác và 684.900 xu được phát hành vào ngày đầu tiên của kỷ nguyên. Khi có 100.000 thợ mỏ đang hoạt động, bình quân đầu người là 6,51 LIGHT/ngày, duy trì "nhận thức số nguyên".
3. **Tính khả thi về hoạt động:** 10% quỹ hoạt động chiến lược (250 triệu xu) để giải quyết khoảng trống phát triển/kiểm toán/tài trợ pháp lý trước TGE ($1,10-2,85 triệu). Mô hình cộng đồng thuần túy không thể bù đắp được chi phí này.
4. **Tính khả thi của giảm phát:** Điểm mấu chốt là 1 tỷ xu sẽ đạt được vào năm thứ 11 đến năm thứ 12 theo kịch bản cơ sở (ngắn hơn 25-30% so với 15 năm+ của kế hoạch 21 tỷ).
5. **Điểm chuẩn hợp lý:** Cùng mức với Filecoin (2 tỷ), nằm trong số năm dự án hàng đầu trong lĩnh vực DePIN theo giá trị thị trường.

### 5.2 Kế hoạch phân phối token

| Hạng mục phân bổ | Tỷ lệ | Số lượng | Mục đích | Phương pháp phát hành |
|----------|------|------|------|---------|
| Khai thác nút nhẹ | 40% | 1 tỷ | Phần thưởng cho người đóng góp mạng lưới | Giảm một nửa sau mỗi 2 năm, phát hành theo thời gian thực dựa trên đóng góp |
| Kho đầu tư doanh nghiệp | 34% | 850 triệu chiếc | Thực hiện đầu tư dưới sự quản trị của DAO (bị phá hủy khi đầu tư) | Khóa đa chữ ký, chỉ được giải phóng và hủy thông qua các nghị quyết hợp lệ |
| Quỹ phát triển sinh thái | 16% | 400 triệu | Thanh khoản, airdrop, tài trợ cho nhà phát triển, hoạt động cộng đồng | Phát hành theo giai đoạn (xem Phần 5.3) |
| Quỹ hoạt động chiến lược | 10% | 250 triệu xu | Đội ngũ, kiểm toán, pháp lý, cơ sở hạ tầng, nhà đầu tư chiến lược | 12 tháng vách + 36 tháng tuyến tính (xem phần 5.X) |

**Đánh giá điểm chuẩn ngành (điểm chuẩn đoàn hệ Tokenomics.net 2024-2025):** Phần thưởng cộng đồng/người dùng 20-35% (LightDAO: khai thác 40% + hệ sinh thái 16% = 56%, cao hơn do không có vòng VC); kho bạc/dự trữ 15-25% (LightDAO: 34%, do chức năng đầu tư); nhóm/nhà đầu tư 15-45% (LightDAO: 10%, thấp hơn nhiều so với ngành, duy trì câu chuyện "National DAO").

### 5.3 Kế hoạch phát hành Quỹ phát triển sinh thái

| Sân khấu | Thời gian | Tỷ lệ | Số lượng | Mục đích |
|------|------|------|------|------|
| TGE | Ngày 0 | 30% | 120 triệu chiếc | Thanh khoản DEX (60%=72 triệu) + airdrop hạt giống (40%=48 triệu) |
| Giai đoạn phát hành tuyến tính 1 | Tháng 1 đến tháng 12 | 40% | 160 triệu xu | 13,33 triệu xu mỗi tháng: khuyến khích cộng đồng, tiếp thị, kế hoạch airdrop |
| Giai đoạn phát hành tuyến tính 2 | ngày 13 đến ngày 24 | 30% | 120 triệu xu | 10 triệu xu mỗi tháng: tài trợ của nhà phát triển, xây dựng sinh thái, dự trữ |

### 5.4 Quỹ hoạt động chiến lược (250 triệu xu)

| Tiểu thể loại | Tỷ lệ | Số lượng | Đối tượng | Quy tắc phát hành |
|--------|------|------|------|----------|
| Dịch vụ trao đổi token | 50% | 125 triệu xu | Các công ty phát triển, tổ chức kiểm toán, công ty luật, nhà điều hành cơ quan xác minh | 12 tháng vách đá + 36 tháng tuyến tính; 30-50% phí dịch vụ thanh toán bằng LIGHT |
| Tài trợ chiến lược | 30% | 75 triệu chiếc | 2-3 Quỹ sinh thái DePIN/Cosmos hoặc các bên chiến lược trong ngành tiêu dùng | Trước TGE được bán với giá 0,03-0,05 USD (thu về 2,25-3,75 triệu USD); 12 tháng vách đá + 24 tháng tuyến tính; nhà đầu tư duy nhất 2% trên tổng số |
| Những người đóng góp cốt lõi | 20% | 50 triệu xu | 3-5 nhà tài trợ/nhà xây dựng cốt lõi | 12 tháng vách đá + 36 tháng tuyến tính; được phát hành dựa trên đánh giá cột mốc hàng quý; không bán trong thời hạn |

**Yêu cầu của nhà đầu tư chiến lược:** Phải cung cấp các khoản đóng góp phi tài chính (một trong các luồng giao dịch, dịch vụ xác minh, tài nguyên tuân thủ) và các nhà đầu tư tài chính thuần túy không được chấp nhận.

**Tuân thủ quy định:** Việc bán trước TGE áp dụng Reg S (nhà đầu tư không phải của Hoa Kỳ) + Quy tắc Reg D 506(c) (nhà đầu tư đủ điều kiện của Hoa Kỳ) miễn trừ theo dõi kép.

**Quy tắc tiết lộ người đóng góp cốt lõi:** Chỉ tổng số tiền (50 triệu = 2% tổng số tiền) và quy tắc phát hành được tiết lộ, tên cá nhân và hạn ngạch cá nhân không được tiết lộ. Các danh mục vai trò được tiết lộ: Công nghệ/Đầu tư/Tuân thủ/Cộng đồng.

### 5.5 Sản lượng khai thác và kế hoạch giảm một nửa

**Đạo hàm:** 2A = 1 tỷ → A = 500 triệu (Kỷ nguyên đầu tiên). Phát hành hàng ngày = 500 triệu ÷ 730 = 684.932 chiếc ≈ 684.900/ngày. Mỗi khối = 684.932->49.371 ≈ 13,87 ÁNH SÁNG.

**Lưu ý:** Tổng phần thưởng cho mỗi khối được chia sẻ cho toàn bộ mạng, trong đó 5% được phân bổ cho người xác thực (34.200/ngày) và 95% được phân bổ cho người khai thác nút nhẹ (650.700/ngày).

| Kỷ nguyên | Thời gian | Tổng sản lượng | Phát hành hàng ngày | Nhóm phần thưởng mỗi khối |
|------|------|---------|----------|-------------|
| Kỷ nguyên thứ nhất | 0-24 tháng | 500 triệu | ≈684,900 | ≈13,87 ÁNH SÁNG |
| Kỷ nguyên thứ 2 | 25-48 tháng | 250 triệu chiếc | ≈342.500 | ≈6,93 ÁNH SÁNG |
| Kỷ nguyên thứ 3 | 49-72 tháng | 125 triệu chiếc | ≈171,200 | ≈3,47 ÁNH SÁNG |
| Kỷ nguyên thứ 4 | 73-96 tháng | 62,5 triệu chiếc | ≈85.600 | ≈1,73 ÁNH SÁNG |
| Kỷ nguyên thứ 5 | 97-120 tháng | 31,25 triệu chiếc | ≈42,800 | ≈0,87 ÁNH SÁNG |

**Kiểm tra:** 5+2,5+1,25+0,625+0,3125+… = 5×2 = 1 tỷ ✓. 97% hoàn thành trong vòng 10 năm đầu tiên.

### 5.6 Mô hình tham chiếu thu nhập của người dùng

| Kích thước mạng | Thu nhập bình quân đầu người hàng ngày | Thu nhập hàng tháng | Thu nhập hàng năm | Thu nhập hàng tháng đầy đủ (1,44 lần) |
|----------|-------------|--------|--------|-------------------|
| 10.000 thợ mỏ (giai đoạn hạt giống) | ≈65.07 | ≈1,952 | ≈23,751 | ≈2,811 |
| 100.000 thợ mỏ (giai đoạn tăng trưởng) | ≈6,51 | ≈195.2 | ≈2,375 | ≈281.1 |
| 1 triệu thợ mỏ (giai đoạn quy mô) | ≈0,65 | ≈19,5 | ≈237,5 | ≈28.1 |

**Cấp độ đối tác (50 lời mời, 20% chia sẻ, toàn bộ tiền thưởng):**

| Quy mô mạng | Bản thân (bao gồm tiền thưởng) | Lời mời chia sẻ | Toàn diện hàng ngày | Toàn diện hàng tháng |
|----------|-------------|---------|--------|--------|
| 10.000 thợ mỏ | ≈93,7 | ≈650,7 | ≈744.4 | ≈22,332 |
| 100.000 thợ mỏ | ≈9,37 | ≈65.07 | ≈74,44 | ≈2,233 |
| 1 triệu thợ mỏ | ≈0,94 | ≈6,51 | ≈7,45 | ≈223.4 |

### 5.7 Kế hoạch tăng trưởng Airdrop

**Mô hình kinh tế:** Tổng ngân sách airdrop = người dùng tiếp cận mục tiêu × airdrop bình quân đầu người × (1+tỷ lệ lãng phí) = 100.000 × 150 LIGHT × 1,3 ≈ 19,5 triệu (loại mua lại) + 35,5 triệu (loại sinh thái) = **55 triệu** (chiếm 13,75% trong quỹ sinh thái 400 triệu).

| Loại thả dù | Điều kiện kích hoạt | Hạn ngạch duy nhất | Ngân sách |
|----------|----------|---------|------|
| Airdrop khai thác đầu tiên | Hoàn thành 4 giờ khai thác hiệu quả lần đầu tiên | 50 ÁNH SÁNG | 15 triệu chiếc |
| Mở rộng về mặt địa lý | Người dùng thị trường mục tiêu hoàn thành ZK-KYC | 100 ÁNH SÁNG | 10 triệu chiếc |
| Học để kiếm tiền | Mô-đun giáo dục hoàn chỉnh + Bài kiểm tra | 30 ÁNH SÁNG | 6 triệu xu |
| Bỏ phiếu Quản trị Đầu tiên | Tham gia bỏ phiếu lần đầu | 20 ÁNH SÁNG | 3 triệu xu |
| Cung cấp thanh khoản | Tiêm LP ≥$50 khóa trong 30 ngày | 200 ÁNH SÁNG | 10 triệu chiếc |
| Sáng tạo nội dung | Hướng dẫn/bản dịch đã được cộng đồng xác minh | 50-200 ÁNH SÁNG | 6 triệu chiếc |
| Kênh hợp tác | Đăng ký + khai thác lần đầu thông qua đối tác | ÁNH SÁNG 80 | 5 triệu chiếc |

**Xác minh CAC:** 55 triệu xu × 0,03 USD = 1,65 triệu USD 30.000 thợ mỏ đang hoạt động được giữ lại = **55 USD/người** (phạm vi ngành là 50-200 USD, ở cấp thấp). Cơ sở học thuật: Zheng (2023) "Chiến dịch Dumbo Drop: Airdrop hay không Airdrop để cung cấp tiền xu ban đầu thành công?" chứng minh rằng tỷ lệ duy trì của airdrop liên quan đến sự kiện gấp 3-5 lần so với airdrop thuần túy.

**Chống lạm dụng:** Dấu vân tay trình duyệt độc đáo + ZK-KYC; giới hạn 1 yêu cầu cho mỗi danh mục cho mỗi địa chỉ; Thời hạn khóa 30 ngày; tái chế tự động mà không có hoạt động trên chuỗi trong vòng 30 ngày sau khi yêu cầu.

### 5.8 Bánh đà động cơ kép và vốn vốn

Bánh đà: Biểu quyết → Phá hủy Vault LIGHT → Thanh toán USDC → Hoàn lại lợi nhuận → Mua lại và phá hủy → Hỗ trợ giá → Nhiều người dùng hơn.

Hệ thống theo dõi kép: kho bạc ổn định (USDC, giữ lợi nhuận) + kho bạc linh hoạt (lớp LIGHT, bị phá hủy khi đầu tư và không chảy vào thị trường). Số lần mua lại được phân chia bằng TWAP, với một lệnh duy nhất 5% khối lượng giao dịch trung bình hàng ngày.

### 5.9 Phát hành và giao dịch token phụ

Tổng số tiền phát hành = số tiền đầu tư 1$; giá trao đổi dựa trên VWAP 30 ngày; tất cả ÁNH SÁNG thu được từ việc trao đổi sẽ bị phá hủy; 50% số người ủng hộ/30% airdrop/20% dự trữ vận hành sẽ được phân phối (khóa trong 6 tháng). Giới hạn cổ tức cho một địa chỉ duy nhất là 15%. Mã thông báo phụ được giao dịch trong AMM trên chuỗi, với thời gian khóa 30 ngày sau khi phát hành và sẽ được đánh dấu là "thanh lý" sau khi rút tiền.

### 5.10 Thanh khoản ban đầu và khám phá giá

**Sắp xếp TGE (Sự kiện tạo mã thông báo, sự kiện tạo mã thông báo): **

| Dự án | Kế hoạch |
|------|------|
| Nhóm thanh khoản ban đầu | Từ 120 triệu phần do quỹ phát triển sinh thái TGE phát hành, 72 triệu phần (60%) đã được phân bổ và bơm vào nhóm thanh khoản DEX |
| Tài sản được ghép nối | USDC (nhóm chính), USDT (nhóm phụ) |
| Thả rơi | 48 triệu còn lại (40%) sẽ được sử dụng để airdrop cho người dùng hạt giống (xem Phần 5.7 Kế hoạch Airdrop) |
| Được niêm yết trên sàn giao dịch | Lần đầu tiên được niêm yết trên các sàn giao dịch phi tập trung (như Osmosis, JunoSwap) sau TGE; đăng ký niêm yết trên sàn giao dịch tập trung bắt đầu từ tháng thứ 6 tùy theo điều kiện tuân thủ |

**Cơ chế chi tiết của Đấu giá kiểu Hà Lan:**

Đấu giá Hà Lan là một phương pháp định giá trong đó giá giảm từ cao xuống thấp. Ngược lại với các cuộc đấu giá ở Anh (nơi giá được đặt từ thấp đến cao), trong cuộc đấu giá ở Hà Lan, người bán đặt giá khởi điểm cao và giá sẽ tự động giảm theo thời gian cho đến khi người mua gửi đăng ký ở một mức giá nhất định. Giá đầu tiên mà tổng số tiền đăng ký đạt mục tiêu là giá mở cửa cuối cùng.

**Tại sao chọn đấu giá kiểu Hà Lan thay vì đấu giá giá cố định hoặc đấu giá kiểu Anh:**

| Định giá | Ưu điểm | Nhược điểm | Khả năng ứng dụng |
|----------|------|------|--------|
| Bán trước giá cố định | Đơn giản | Việc định giá mang tính chất chủ quan, cao quá thì không bán được, thấp quá thì bị robot chộp lấy | Không phù hợp (không có chức năng dò giá) |
| Đấu giá Anh (đấu thầu) | Khám phá giá đầy đủ | Những người mua lớn có thể chờ đợi và tăng giá một cách có chiến lược; chiến tranh khí đốt | Không phù hợp (cuộc chiến gas trên chuỗi không bao gồm người dùng nhỏ) |
| **Đấu giá Hà Lan** | ** Tự động phát hiện giá; không cần đấu thầu (không có chiến tranh khí đốt); sự tham gia bình đẳng của người mua lớn và nhỏ; chống bot (cơ chế giảm giá tự nhiên ức chế việc chạy trước)** | Giá khởi điểm và tốc độ giảm tốc cần được đặt hợp lý | **Thích hợp nhất (công bằng + hiệu quả + chống thao túng)** |

**Thông số cụ thể của phiên đấu giá LightDAO Hà Lan:**

| Thông số | Cài đặt | Mô tả |
|------|------|------|
| Mục tiêu đấu giá | Token LIGHT (được phân bổ từ 72 triệu do quỹ sinh thái TGE phát hành) | USDC từ cuộc đấu giá sẽ được bơm vào kho ổn định |
| Số tiền gây quỹ mục tiêu | **15 triệu USDC** | 5 triệu USD → dự trữ tối thiểu của kho bạc ổn định; 10 triệu USD → vốn đầu tư ban đầu |
| Giá khởi điểm | $0,20/ÁNH SÁNG | Cao hơn giá cân bằng dự kiến, đảm bảo không bị mất giá trong vài giây |
| Tốc độ giảm tốc | Giảm 5% mỗi giờ | Bắt đầu từ 0,20 USD, giảm xuống 0,017 USD sau khoảng 48 giờ (nếu không có ai đăng ký) |
| Giá khởi điểm tối thiểu | 0,01 USD/ÁNH SÁNG | Nếu hạ giá khởi điểm mà vẫn chưa đạt mục tiêu, cuộc đấu giá sẽ bị hoãn lại 24 giờ hoặc số lượng đồ vật sẽ được điều chỉnh |
| Phương thức đăng ký | Người dùng gửi "Tôi sẵn sàng mua X USDC LIGHT tương đương với mức giá hiện tại" | Không cần đấu thầu, hệ thống sẽ quyết toán theo giá thống nhất cuối cùng (phần vượt quá sẽ được hoàn trả mà không phải đền bù) |
| Giới hạn trên của một người dùng | Không quá 5% số tiền gây quỹ mục tiêu (tức là 750.000 USD) | Ngăn chặn một người mua độc quyền số chip ban đầu |
| Yêu cầu KYC | Xác minh nâng cao (Cư trú thuế) | Yêu cầu tuân thủ |

**Nguồn vốn từ kết quả đấu giá:**

```
用户认购总额 $1,500万 USDC
    ├── $500万 → 稳定金库（最低储备，覆盖运营+应急）
    └── $1,000万 → 初始投资资本（稳定金库中可部署部分）

拍卖售出的LIGHT → 买家钱包（进入流通）
未售出的LIGHT（若有）→ 注入DEX流动性池
```

**Thời gian bảo vệ phát hiện giá:** Bộ ngắt mạch biến động giá được thiết lập trong 72 giờ đầu tiên sau TGE - nếu giá giao dịch DEX chênh lệch hơn ±50% so với giá mở phiên đấu giá, chức năng trao đổi mã thông báo phụ sẽ bị tạm dừng (khai thác và chuyển giao sẽ không bị ảnh hưởng) để ngăn chặn hoạt động đầu cơ cực đoan cản trở quá trình khởi động sinh thái. Cầu chì sẽ tự động ngắt sau 72 giờ.

**Tại sao là 15 triệu USD thay vì thấp hơn:** Vốn đầu tư ban đầu là 10 triệu USD cần hỗ trợ 3-5 khoản đầu tư trong năm đầu tiên (một khoản đầu tư duy nhất là 2-5 triệu USD, xem quy mô của giai đoạn khởi nghiệp ở Phần 9.1). Nếu chỉ huy động được 5 triệu USD (tất cả đều là dự trữ), sẽ không có vốn đầu tư có thể triển khai trong năm đầu tiên và bánh đà sẽ không khởi động. 15 triệu USD = dự trữ 5 triệu USD + đầu tư 10 triệu USD, đây là mức cân bằng khả thi tối thiểu giữa "điểm mấu chốt an toàn" và "khởi động bánh đà".

### 5.11 Cơ chế giảm phát và điểm mấu chốt

**Khối lượng lưu thông = phát hành khai thác + phát hành sinh thái + quỹ chiến lược được phát hành − trao đổi và tiêu hủy − tiêu hủy khí − mua lại và tiêu hủy. ** 850 triệu xu từ kho đầu tư chưa bao giờ được đưa vào lưu thông. Giới hạn lưu thông trên lý thuyết = 10+4+2,5 = **1,65 tỷ**.

| Điều kiện kích hoạt | Hành vi hệ thống |
|----------|----------|
| Lưu hành ≤ 1,5 tỷ chiếc | Tín hiệu giảm tốc độ (kịch bản phá hủy cực thấp) |
| Khối lượng lưu hành ≤ 1,2 tỷ chiếc | Thông báo cảnh báo sớm, tạm dừng hoạt động tiêu diệt (khoảng năm thứ 8 của kịch bản cơ sở) |
| Khối lượng lưu hành ≤ 1 tỷ | Dừng cứng, tất cả các khu hủy diệt đều bị đóng cửa vĩnh viễn (kịch bản cơ bản là vào khoảng năm 11-12) |

### 5.12 Cơ chế bình ổn giá (vòng xoáy chống tử thần)

**Nguyên tắc cốt lõi:** LightDAO không can thiệp vào việc khám phá giá thị trường hàng ngày. Giao thức chỉ điều chỉnh các tham số của nó trong các tình huống cực kỳ đi xuống để giảm nguy cơ rơi vào “vòng xoáy tử thần”.

**Logic phân loại:** Trong các môi trường dễ biến động khác nhau, cùng một mức giảm thể hiện mức độ bất thường khác nhau. Sự sụt giảm mạnh trong thị trường có độ biến động thấp là tín hiệu bất thường mạnh hơn và cần sự can thiệp ở cường độ cao hơn; sự sụt giảm mạnh trong một thị trường có biến động cao là tương đối phổ biến và có thể sử dụng biện pháp can thiệp nhẹ nhàng hơn. Do đó, cường độ can thiệp có quan hệ thuận chiều với sự bất thường của tín hiệu chứ không chỉ phụ thuộc vào giá trị tuyệt đối của sự suy giảm.

**Biểu đồ đầy đủ của cơ chế:**

| Tình trạng thị trường | Biến động lịch sử 30 ngày | Điều kiện kích hoạt | Mức tín hiệu | Thực thi sau khi kích hoạt | Điều kiện phục hồi |
|----------|--------------|---------|----------|----------|----------|
| Biến động thấp | 30% | Giảm tích lũy ≥40% trong 5 ngày liên tiếp | Cấp I | Sản lượng khai thác giảm 50%; tỷ lệ phá hủy tăng từ 20% lên 35%; thời gian công khai điều chỉnh thông số rủi ro được rút ngắn từ 72h xuống còn 12h; ủy ban bóng tối đã chuyển sang trạng thái hoạt động (chỉ có thể thực hiện quyền đình chỉ tạm thời theo quy định của pháp luật) | Giá đứng trên đường trung bình động 30 ngày và bật trở lại ≥80% so với giá kích hoạt và duy trì như vậy trong 10 ngày liên tiếp |
| Biến động trung bình | 30%-60% | Giảm tích lũy trong 7 ngày liên tiếp ≥ 50% | Cấp II | Sản lượng khai thác giảm 50%; tỷ lệ phá hủy tăng từ 20% lên 30%; thời gian công khai được rút ngắn xuống còn 24 giờ; ủy ban bóng tối bước vào trạng thái hoạt động | Giá đứng trên đường trung bình động 30 ngày và bật trở lại ≥ 60% so với giá kích hoạt và duy trì như vậy trong 7 ngày liên tiếp |
| Biến động cao | 60%-100% | 10 ngày liên tiếp giảm tích lũy ≥55% | Cấp III | Sản lượng khai thác giảm tới 75%; tỷ lệ phá hủy tăng từ 20% lên 25%; thời gian công khai được rút ngắn xuống còn 48 giờ; ủy ban bóng tối vào chế độ chờ | Giá đứng trên đường trung bình động 30 ngày và bật trở lại ≥40% so với giá kích hoạt và duy trì như vậy trong 5 ngày liên tiếp |
| Biến động cực độ | >100% | Giảm tích lũy trong 10 ngày liên tiếp ≥ 65% | Cấp III | Thực hiện theo các biện pháp Cấp III về mức độ biến động cao | Được thực hiện theo điều kiện phục hồi Cấp III cho độ biến động cao |

**Điều kiện loại trừ:** Chỉ khi mức giảm của Bitcoin trong cùng thời kỳ nhỏ hơn 50% mức giảm của LIGHT, cơ chế trên mới có thể được kích hoạt để loại trừ sự sụp đổ thị trường có hệ thống (tức là nếu BTC cũng giảm mạnh trong cùng thời kỳ thì đó là một sự kiện thị trường tổng thể và không có sự can thiệp riêng biệt nào được thực hiện đối với LIGHT).

**Mô tả logic phục hồi:** Yêu cầu và thời lượng phục hồi giảm theo mức độ bất thường: Cấp I yêu cầu biên độ phục hồi cao nhất (80%) và thời gian xác nhận dài nhất (10 ngày), trong khi Cấp III yêu cầu yêu cầu tương đối thấp hơn (40%/5 ngày). Sự sắp xếp này phù hợp với logic lũy tiến là “tín hiệu bất thường càng mạnh thì sự can thiệp càng mạnh và xác nhận phục hồi càng chặt chẽ”.

**Nguồn dữ liệu về biến động và giá cả:** Biến động lịch sử trong 30 ngày và mức giảm tích lũy được cung cấp bởi nhà tiên tri về giá trên chuỗi (xem Phần 4.10), dựa trên ảnh chụp nhanh TWAP của khối UTC 00:00 hàng ngày và không dựa vào bất kỳ nguồn dữ liệu bên ngoài nào.

### 5.13 Thử nghiệm căng thẳng về tính bền vững của thu nhập

| Kịch bản căng thẳng | Điều gì xảy ra | Phản hồi giao thức | Kết quả trường hợp xấu nhất |
|----------|----------|---------|---------|
| Tất cả các khoản đầu tư đều thất bại | Tất cả các công ty đầu tư đều thua lỗ hoặc không thoát ra được | Quỹ bảo hiểm (10% lợi nhuận tích lũy) bù đắp một phần tổn thất; dự trữ ngân quỹ ổn định ( ≥ 8 triệu USD) để duy trì hoạt động; các khoản đầu tư mới bị đình chỉ cho đến khi cộng đồng đánh giá lại | Người nắm giữ mã thông báo phụ không thể nhận cổ tức; Giá LIGHT chịu áp lực nhưng không trở về 0 (chức năng khai thác và quản trị tiếp tục hoạt động) |
| Thị trường lao dốc 80% | Giá LIGHT giảm 80% so với đỉnh | Kích hoạt cơ chế xoắn ốc chống tử thần (cấp II hoặc cấp III); sản lượng khai thác giảm 50-75%; tỷ lệ phá hủy được tăng lên; ủy ban bóng tối có thể đình chỉ các hoạt động có rủi ro cao | Thu nhập của người dùng giảm nhưng mạng vẫn tiếp tục hoạt động; cơ chế tự động dỡ bỏ khi đáp ứng đủ điều kiện phục hồi |
| Lệnh cấm quy định thị trường lớn | Một quốc gia lớn đã cấm hoàn toàn tài sản tiền điện tử | Gương IPFS chuyển đổi mặt trước vẫn có thể truy cập được; tài sản trên chuỗi cũng như quyền và lợi ích hiện tại của người dùng không bị ảnh hưởng; tính khả dụng của dịch vụ bên thứ ba chỉ được điều chỉnh trong phạm vi thực thi pháp luật; Hoạt động của SPV tại Quần đảo Cayman không thuộc thẩm quyền của một quốc gia duy nhất | Tăng trưởng người dùng trong khu vực đã bị đình trệ; các khu vực khác trên thế giới không bị ảnh hưởng |
| Mất người dùng quy mô lớn | Công cụ khai thác đang hoạt động giảm hơn 70% | BaseReward được tự động phân phối lại (mẫu số co lại → thu nhập bình quân đầu người của người dùng giữ lại tăng); khuyến khích lời mời có trọng số để thu hút dòng tiền quay trở lại; ngưỡng quản trị tạm thời được hạ xuống (cơ chế động ở Mục 5.14) | An ninh mạng bị giảm nhưng chuỗi sẽ không bị dừng (Tendermint BFT chấp nhận <1/3 trình xác thực ngoại tuyến) |
| Lỗ hổng hợp đồng thông minh lớn | Lỗ hổng có thể khai thác được tìm thấy trong các hợp đồng cốt lõi | Đình chỉ khẩn cấp nhiều chữ ký đối với dòng tiền chảy ra (khóa thời gian 72 giờ cung cấp thời gian phản hồi); Bắt đầu bỏ phiếu di chuyển hợp đồng dự phòng (sửa chữa khẩn cấp cấp độ L4, xem Phần 4.12); Quỹ bảo hiểm chi trả cho những tổn thất của người dùng | Một số quỹ có thể bị hư hỏng; Hoạt động bình thường sẽ tiếp tục sau khi quá trình di chuyển hoàn tất |

### 5.14 Cơ chế cân bằng giữa các thế hệ

Điều chỉnh linh hoạt ngưỡng quản trị: cứ 1 triệu công cụ khai thác tích lũy mới đang hoạt động, ngưỡng đề xuất sẽ tự động giảm 5% (giới hạn dưới 2.500 LIGHT).

> **[Các thuật ngữ trong chương này]**
> **TGE** (Sự kiện tạo mã thông báo): Thời điểm mã thông báo lần đầu tiên được tạo và phân phối thông qua hợp đồng thông minh, thường đi kèm với việc thiết lập nhóm thanh khoản ban đầu, định giá đấu giá kiểu Hà Lan và giao dịch công khai đầu tiên. Tương tự như IPO trong tài chính truyền thống, nhưng không liên quan đến việc niêm yết trên sàn giao dịch chứng khoán.
> **Halving** (Halving): Một cơ chế theo đó sản lượng khai thác tự động giảm 50% sau mỗi khoảng thời gian cố định (2 năm/730 ngày đối với LightDAO). Mục đích là tạo ra sự khan hiếm ngày càng tăng - theo thời gian, nguồn cung mới được thêm vào ngày càng ít và nếu nhu cầu không giảm thì giá sẽ được hỗ trợ. Bitcoin áp dụng giảm một nửa cứ sau 4 năm.
> **Kho bạc** (Kho bạc): Dự trữ mã thông báo bị khóa bởi các hợp đồng nhiều chữ ký, chỉ có thể được giải phóng thông qua các nghị quyết quản trị. LightDAO có hai loại kho tiền: kho tiền đầu tư (giữ LIGHT và bị phá hủy khi khoản đầu tư được thực hiện) và kho tiền ổn định (giữ USDC và được sử dụng để thanh toán chi phí hoạt động và xem xét đầu tư).
> **Giảm phát** (Giảm phát): Quá trình trong đó tổng nguồn cung hoặc lưu thông token tiếp tục giảm. LightDAO đạt được giảm phát thông qua bốn cơ chế: thực hiện và hủy đầu tư, trao đổi và hủy mã thông báo phụ, hủy phí gas (50%) và mua lại và hủy lợi nhuận.
> **Vòng xoáy tử thần** (Vòng xoáy tử thần): Giá token giảm → thu nhập của người khai thác giảm → người khai thác bỏ việc → an ninh mạng/đóng góp giảm → mất niềm tin hơn nữa → một vòng luẩn quẩn trong đó giá tiếp tục giảm. Cơ chế can thiệp theo cấp độ trong Phần 5.12 được thiết kế để làm gián đoạn chu trình này.
> **Mã thông báo phụ** (Mã thông báo phụ): Giấy chứng nhận yêu cầu phân phối thu nhập SPV được cấp theo quy định sau khi mỗi khoản đầu tư của công ty hoàn thành (chẳng hạn như mua lại thương hiệu cà phê → mã thông báo CAFE). Nắm giữ mã thông báo phụ = nắm giữ tư cách để phân phối lợi nhuận trong tương lai và không đại diện cho quyền của cổ đông hoặc quyền quản trị doanh nghiệp.
> **LP** (Nhà cung cấp thanh khoản): Những người tham gia đưa hai tài sản có giá trị như nhau (chẳng hạn như LIGHT+USDC) vào nhóm thanh khoản DEX sẽ kiếm được phí giao dịch. LP là cơ sở cho hoạt động bình thường của DEX.
> **VWAP** (Giá trung bình tính theo khối lượng): Giá trong một khoảng thời gian được tính theo khối lượng của mỗi giao dịch, phản ánh chi phí giao dịch thực tế trên thị trường. LightDAO sử dụng VWAP 30 ngày làm chuẩn định giá cho việc trao đổi mã thông báo phụ.
> **CAC** (Chi phí thu nạp khách hàng, chi phí thu nạp người dùng): Chi phí trung bình để thu nạp một người dùng đang hoạt động hiệu quả. CAC mục tiêu của chương trình airdrop LightDAO là 55 USD/máy khai thác đang hoạt động được giữ lại (phạm vi ngành là 50-200 USD).
> **wLIGHT** (LIGHT được bao bọc, LIGHT được đóng gói): Token tương đương với LIGHT được phát hành trên Ethereum hoặc Solana thông qua các cầu nối chuỗi chéo và một lượng LIGHT gốc tương đương bị khóa theo hợp đồng cầu nối dưới dạng dự trữ 1:1. Mục đích là cho phép người dùng không thuộc hệ sinh thái Cosmos có được và nắm giữ ÁNH SÁNG.
> **Đấu giá kiểu Hà Lan** (Đấu giá kiểu Hà Lan): Một phương thức định giá trong đó giá giảm từ cao xuống thấp. Người bán đặt giá khởi điểm cao và giá sẽ tự động giảm theo thời gian cho đến khi người mua gửi đăng ký ở một mức giá nhất định. Giá đầu tiên mà tổng số tiền đăng ký đạt mục tiêu là giá giao dịch cuối cùng. Ưu điểm là không cần đấu thầu (không có chiến tranh khí đốt), người mua ở mọi quy mô đều bình đẳng và nó có khả năng chống lại sự chiếm ưu thế của robot một cách tự nhiên.

---

## Chương 6: Cơ chế quản trị

### 6.1 Mô hình biểu quyết hai chiều

Trọng số nắm giữ tiền tệ (bao gồm danh tiếng + tiền thưởng cấp độ, tổng giới hạn trên +40%) + số lượng địa chỉ (1 địa chỉ = 1 phiếu bầu, địa chỉ liên quan được hợp nhất). Quyền biểu quyết có hiệu lực trong 90 ngày và có thể được kích hoạt bằng cách chuyển 5 ĐÈN. Phần thưởng danh tiếng: Giữ tiền trong 1 năm + 15 phiếu bầu hợp lệ → lên tới +30%.

### 6.2 Tốc độ vượt qua động

Tỷ lệ đậu tối thiểu = 50% + (50% - tỷ lệ bỏ phiếu thực tế). Đa số đơn giản khi tỷ lệ biểu quyết ≥50%.

### 6.3 Tham số đề xuất

| Loại | Ký quỹ | Tỷ lệ biểu quyết mã thông báo | Tỷ lệ biểu quyết địa chỉ | Tỷ lệ đậu | Trì hoãn thực hiện |
|------|--------|----------|----------|--------|----------|
| Vi mô | $100 | ≥15% | ≥20% | Năng động ≥55% | 24h |
| Loại mua lại | $500 | ≥25% | ≥30% | Năng động ≥60% | 72h |
| Loại hình đầu tư mạo hiểm | $500 | ≥35% | ≥40% | Năng động ≥60% | 72h |
| Thiếu tá | 1.000 USD | ≥45% | ≥50% | Năng động ≥66% | 72h |
| Khẩn cấp | 2.000 USD | ≥50% | ≥60% | ≥75% | Không cấp vốn 6h/1h rủi ro cao; hoạt động vốn vẫn bị khóa thời gian 72h |

### 6.4 Vòng đời đề xuất

Điều kiện nộp hồ sơ: ≥5.000 LIGHT + 30 ngày cam kết + đặt cọc liên tục. Thông báo công khai 72h (sửa đổi 2 lần). Việc bỏ phiếu diễn ra trong vòng 7 ngày (48 giờ đối với đường đua nhanh, 500.000 USDC). Phủ quyết hạ nhiệt trong 90 ngày. Hiệu quả bị trì hoãn trong 24 giờ.

**Mô tả ngưỡng:** 5.000 xu trong giai đoạn hạt giống (10.000 thợ mỏ) ≈ 77 ngày sản lượng cơ bản; cấp độ đối tác ≈ 7 ngày. Quản trị sẽ được kích hoạt vào tháng thứ bảy và những người dùng sớm sẽ có đủ thời gian tích lũy.

### 6.5 Ưu đãi bầu cử

Có khuyến khích cơ bản cho việc tham gia (thậm chí chia sẻ) và có phần thưởng bổ sung cho phán đoán chính xác (50% tổng số tiền cá cược). Đặt cược vào phạm vi 5-500 LIGHT. Ngăn chặn hiệu ứng bầy đàn: Đối thủ vẫn nhận được những ưu đãi cơ bản ngay cả khi họ “vào nhầm đội”.

### 6.6 Thưởng và phạt khi thành công hay thất bại

Thất bại vì thiện chí: hoàn lại 50% tiền đặt cọc + thời gian hồi chiêu 30 ngày. Lỗi cố ý (giả mạo/lặp lại): tịch thu toàn bộ số tiền + cấm vĩnh viễn. Bằng chứng gian lận: giới hạn ở mức 5.000 LIGHT, phạt 40% tiền thưởng thành lập + 500 LIGHT.

### 6.7 Minh bạch tài chính

Bảng điều khiển thời gian thực trên chuỗi + báo cáo tài chính hàng quý + kiểm toán độc lập hàng năm (lần kiểm toán đầu tiên phải được hoàn thành trước TGE) + công bố mục tiêu đầu tư theo thời gian thực.

---

## Chương 7: Kiểm tra, cân bằng quyền lực và xác định vai trò

### 7.1 Người giám hộ ban đầu

Quyền được giới hạn đối với tài liệu/định dạng/thông tin trang web chính thức. Thời hạn ≤ 24 tháng. Một người giám hộ thay thế phải được chỉ định (không thể ký trong 30 ngày liên tiếp → tự động được đảm nhận). Khuyết tật đồng thời → Bỏ phiếu khẩn cấp 48h để bổ nhiệm người quản lý tạm thời.

### 7.2 Lộ trình chuyển giao quyền lực

| Sân khấu | Thời gian | Quyền | Phê duyệt đầu tư |
|------|------|------|----------|
| Thời kỳ sáng tạo | 0-6 tháng | Người giám hộ (phi tài chính) | Người giám hộ + cộng đồng đa chữ ký 3/5 |
| Giai đoạn chuyển tiếp | Tháng 7-Tháng 12 | Người giám hộ + cộng tác viên cốt lõi cùng ký | Tương tự như trên + người đóng góp cốt lõi |
| Thời gian đáo hạn | 13-24 tháng | Ủy ban Quản trị 3/5 | Bỏ phiếu hai chiều thông thường |
| Thời kỳ tự chủ | 25 tháng + | Tất cả người nắm giữ | Cùng kỳ hạn |

### 7.3 Ban quản trị

Quyền lực được chia cho 5 người (luân phiên chủ tịch/tài chính/công nghệ/cộng đồng/chủ chốt), luân phiên hàng quý, nhiệm kỳ 6 tháng và có thể tái cử một lần. Chiến dịch cam kết 50.000 chữ ký chung LIGHT + 100 địa chỉ. Việc ra quyết định có sự tham gia của ≥3 người và bao gồm ≥3 vị trí.

**Mô tả ngưỡng:** 50.000 xu trong giai đoạn hạt giống ≈ 67 ngày (2,2 tháng) cho đối tác; trong giai đoạn tăng trưởng ≈ 672 ngày (22 tháng). Cuộc bầu cử ủy ban đầu tiên vào tháng thứ 13 dành cho các đối tác sớm.

### 7.4 Ủy ban Bóng tối

Đình chỉ tạm thời chỉ vì "vi phạm/xử phạt/gian lận lớn". Tất cả các phiếu bầu phải được phê chuẩn trong vòng 72 giờ (phản đối >60%→bác bỏ). Bị từ chối hai lần liên tiếp → tự động bị luận tội và giải tán.

### 7.5—7.6 Xác minh chiến dịch và kế hoạch chính

SimHash>80% bị loại; Nội dung AI phải được bổ sung phần giải thích; 20% phiếu bầu sẽ bị trừ cho những câu hỏi vắng mặt. Sao lưu phân đoạn khóa + kiểm tra tình trạng hàng quý + thông báo công khai trong 7 ngày + thay thế phiếu bầu.

---

## Chương 8: Cơ chế tin cậy và bảo mật

### 8.1 Năm cơ chế bảo mật chính

Thời gian khóa 72h (đề xuất khẩn cấp không được miễn hoạt động vốn); ký nhiều lần 3/5; luân chuyển hàng quý ≤ 2 buổi; Phạt 100% tội gian lận; tất cả các giao dịch đều trên chuỗi.

### 8.2 Quỹ bảo hiểm

**10%** lợi nhuận đầu tư thành công được tích lũy. Các yêu cầu bồi thường phải được báo cáo độc lập + DAO 66% ủng hộ + một nhóm 20%. Nguồn bổ sung: 30% tiền phạt làm giả. Định vị "bộ đệm một phần" không được bảo vệ hoàn toàn.

### 8.3 Kế hoạch cực đoan

Giám sát thiên nga đen → IPFS + loại bỏ quyền quản trị viên; gian lận → đình chỉ ủy ban bóng tối (phê chuẩn 72h) + quỹ bảo hiểm + trọng tài SPV; vòng xoáy tử thần → Cơ chế mục 5.12; lỗ hổng hợp đồng → đình chỉ đa chữ ký + bỏ phiếu di chuyển; người xác thực cùng nhau làm điều ác → Dung sai BFT <1/3, nếu vượt quá, chuỗi sẽ bị đình chỉ + di chuyển bỏ phiếu khẩn cấp.

---

## Chương 9: Hoạt động đầu tư và chiến lược rút lui

### 9.1 Sàng lọc và quy mô mục tiêu đầu tư

**Quỹ đạo tăng trưởng theo từng giai đoạn của quy mô đầu tư (công thức: thặng dư kho bạc × 15% × giá LIGHT): **

| Sân khấu | giá ÁNH SÁNG | Hạn mức giao dịch một lần trong thời gian đầu của vault | Mục tiêu thích ứng | Điểm chuẩn ngành |
|------|----------|------------------|----------|----------|
| Giai đoạn khởi nghiệp (Y1-2) | 0,02 USD—0,05 USD | 2,55 triệu USD—6,37 triệu USD | Cửa hàng đơn lẻ/chuỗi nhỏ, vòng thiên thần | PE siêu nhỏ |
| Giai đoạn tăng trưởng (Y3-5) | 0,05 USD—0,30 USD | 6,37 triệu USD—38,25 triệu USD | Chuỗi khu vực 30-200 cửa hàng, vòng Seed-A | Thị trường trung lưu PE |
| Giai đoạn trưởng thành (Y5-8) | $0,30—$1,00 | 38,25 triệu USD—127,5 triệu USD | Chuỗi đa quốc gia/công nghệ quy mô vừa, vòng B-C | Thị trường trung bình PE |
| Giai đoạn quy mô (Y8+) | $1,00+ | 127,5 triệu USD+ | Mua lại quy mô lớn, Trước IPO | PE quy mô lớn/VC giai đoạn tăng trưởng |

### 9.2 Quá trình ra quyết định đầu tư

Khám phá dự án ( ≥5.000 LIGHT) → thẩm định độc lập → thông báo công khai 72h → bỏ phiếu hai chiều → thực hiện 24/72h.

### 9.3 Thoát ra và phân phối lợi nhuận

Cổ tức hàng năm: **40%** chủ sở hữu mã thông báo phụ / **30%** kho tiền ổn định / **20%** mua lại LIGHT để tiêu hủy / **10%** quỹ bảo hiểm.
Thu nhập thoát: **70%** Stable Vault / **30%** Mua lại và đốt.

### 9.4 Kỷ luật đầu tư

| Nội quy | Nội dung |
|------|------|
| Giới hạn phá hủy đơn | Vault còn lại × 15% (850 triệu × 15% ban đầu = 127,5 triệu xu) |
| Mục tiêu duy nhất | 25% tổng giá trị kho tiền |
| Sự tập trung của ngành | 40% danh mục đầu tư |
| Sự tập trung về mặt địa lý | 30% danh mục đầu tư |
| Dự trữ kho bạc ổn định | 5 triệu USD tại TGE (đấu giá), đạt 8 triệu USD vào tháng thứ 24 |
| Thời gian nghỉ mát | 2 lần thất bại liên tiếp → 180 ngày |

**Sức chứa kho tiền:** 850 triệu sản phẩm × 0,10 USD = 85 triệu USD (tổng công suất ban đầu); × 0,30 USD = 255 triệu USD; × 1,00 USD = 850 triệu USD. Giới hạn giao dịch duy nhất 15% khiến tốc độ đầu tư có liên quan tích cực đến giá cả.

> **[Các thuật ngữ trong chương này]**
> **EBITDA** (Thu nhập trước lãi vay, thuế, khấu hao và khấu hao): Một chỉ số đo lường khả năng sinh lời của các hoạt động cốt lõi của công ty, loại bỏ sự can thiệp của cấu trúc tài chính (lãi suất), chính sách thuế (thuế) và các lựa chọn kế toán (khấu hao/khấu hao), tạo điều kiện thuận lợi cho việc so sánh giữa các doanh nghiệp và giữa các ngành. Tỷ suất lợi nhuận EBITDA = EBITDA thu nhập hoạt động.
> **DCF** (Dòng tiền chiết khấu, phương pháp dòng tiền chiết khấu): Phương pháp định giá chuyển đổi dòng tiền dự kiến ​​trong tương lai của công ty thành giá trị hiện tại ở một tỷ lệ chiết khấu nhất định. Nó phù hợp với các doanh nghiệp trưởng thành với dòng tiền ổn định (chẳng hạn như chuỗi tiêu dùng), nhưng không phù hợp với các công ty công nghệ giai đoạn đầu chưa có lãi.
> **IPO** (Chào bán lần đầu ra công chúng): Lần đầu tiên một công ty phát hành cổ phiếu ra công chúng trên sàn giao dịch chứng khoán và được niêm yết để giao dịch. Đối với LightDAO, IPO của các công ty được đầu tư là một trong những lối thoát chính cho các động cơ tăng trưởng.
> **Trước IPO**: Vòng huy động vốn cổ phần tư nhân cuối cùng trước khi công ty chính thức niêm yết. Thông thường mức định giá gần bằng mức sau IPO, rủi ro thấp hơn các vòng trước nhưng bội số lợi nhuận cũng thấp hơn.
> **Thực thi TWAP** (Thực thi giá trung bình theo trọng số thời gian): Chia các lệnh mua lại số lượng lớn thành nhiều lệnh số lượng nhỏ và thực hiện chúng một cách đồng đều trong một khoảng thời gian để tránh tác động của một lệnh lớn duy nhất lên giá thị trường. LightDAO quy định rằng một lần mua lại không được vượt quá 5% khối lượng giao dịch trung bình hàng ngày.

---

## Chương 10: Lộ trình

| Giai đoạn | Thời gian | Mục tiêu cốt lõi | Các cột mốc quan trọng | Điều kiện tiên quyết |
|------|------|---------|----------|----------|
| Giai đoạn chuẩn bị | Quý 4 năm 2026 | Pháp nhân + đội ngũ + quỹ hiện có | Hoàn tất đăng ký thực thể Cayman/BVI; đối tác kỹ thuật hoặc nhóm phát triển đã ký kết; ý định của nhà đầu tư chiến lược đã được xác nhận (2-3 công ty); vốn khởi nghiệp ≥ 150.000 USD | người sáng lập xác định phương pháp tiết lộ danh tính; hoàn thành BP và Pitch Deck |
| Thời kỳ phát triển | Q1-Q2 2027 | Phát triển hệ thống cốt lõi | 10 mô-đun hợp đồng thông minh đã được phát triển; Việc phát triển giao diện người dùng PWA đã được hoàn thành; 7 mạng thử nghiệm xác minh đã được triển khai; thử nghiệm Alpha nội bộ đã vượt qua | Đội ngũ phát triển tại chỗ; tài liệu yêu cầu (Thông số kỹ thuật) đã hoàn thiện |
| Giai đoạn kiểm tra và thử nghiệm | Quý 3 năm 2027 | Xác minh bảo mật và tuân thủ | Phát hành báo cáo kiểm toán an ninh độc lập ( ≥1 tổ chức hàng đầu); phát hành phiếu lấy ý kiến ​​tuân thủ pháp luật (MLM + luật chứng khoán); 50.000 bài kiểm tra căng thẳng đồng thời đã được thông qua; hệ thống chống gian lận tỷ lệ dương tính giả <2%; bài tập biểu quyết quản trị đã hoàn thành | Đóng băng phát triển hợp đồng (Code Freeze); phí kiểm toán tại chỗ |
| TGE và mạng chính trực tuyến | Quý 4 năm 2027 | Phát hành mã thông báo + khởi chạy mạng | Cuộc đấu giá ở Hà Lan đã hoàn tất (mục tiêu 15 triệu USD); mainnet trực tuyến ( ≥10 trình xác nhận); nền tảng khai thác mở cửa cho công chúng; Nhóm thanh khoản DEX được thành lập; phát hành airdrop hạt giống | Kiểm toán đã được thông qua; trình xác nhận ≥7 (dòng cuối cùng); triển khai hợp đồng đấu giá |
| Giai đoạn xây dựng niềm tin | Q1 2028 (Tháng 1 đến tháng 3 sau TGE) | 30.000-50.000 người dùng hạt giống | Máy khai thác đang hoạt động vượt quá 30.000; thực hiện bỏ phiếu quản trị lần đầu; kênh cộng đồng đa ngôn ngữ được thành lập (tiếng Anh/Trung Quốc/Tây Ban Nha/Bồ Đào Nha/Philippines); báo cáo cộng đồng hàng tháng đầu tiên được phát hành | TGE đã hoàn thành; đội ngũ hoạt động cộng đồng tại chỗ |
| Thời kỳ neo giá trị | Q2-Q3 năm 2028 (tháng thứ 4 đến thứ 9 sau TGE) | Đầu tư lần đầu + quản trị thời kỳ chuyển tiếp | Đề xuất đầu tư đầu tiên được thông qua (phê duyệt nhiều chữ ký trong giai đoạn khởi đầu áp dụng từ tháng thứ 4 đến tháng thứ 6; phê duyệt chung trong giai đoạn chuyển tiếp áp dụng từ tháng thứ 7); đợt giao hàng SPV đầu tiên đã hoàn tất; người xác nhận được mở để bầu cử (từ tháng thứ 7); báo cáo tài chính quý đầu tiên được công bố | kho bạc ổn định USDC ≥ 5 triệu USD; thẩm định mục tiêu đầu tư đã hoàn thành |
| Thời hạn quản trị | 2028 Q4-2029 Q1 (Tháng 10 đến tháng 15 sau TGE) | Bầu cử ủy ban + chuyển đổi phân cấp | Bầu cử ban quản trị lần thứ nhất (tháng thứ 13); Bước vào thời kỳ đáo hạn (quyết định 3/5 của hội đồng); Cầu chuỗi chéo wLIGHT đi vào hoạt động trực tuyến; Đơn đăng ký niêm yết CEX được nộp; Kế hoạch tài trợ của nhà phát triển bắt đầu | Thợ mỏ đang hoạt động ≥ 100.000; ≥ 100 địa chỉ ứng viên chung |
| Thời kỳ mở rộng sinh thái | Bắt đầu từ quý 2 năm 2029 (tháng thứ 16 + sau TGE) | Nhân rộng quy mô lớn | Máy khai thác đang hoạt động vượt quá 200.000-500.000; 2-3 khoản đầu tư đã hoàn thành; xác minh hồi hương lợi nhuận đầu tiên; Bắt đầu mua lại và tiêu hủy LIGHT | Ban quản trị đang hoạt động bình thường; mô hình đầu tư đã được kiểm chứng |
| Thời kỳ hoạt động trưởng thành | Bắt đầu từ Quý 4 năm 2029 (tháng thứ 25 + sau TGE) | Xoay bánh đà + tự chủ hoàn toàn | Bước vào thời kỳ tự chủ (đề xuất lớn từ tất cả các chủ sở hữu); triển khai danh mục đầu tư tích lũy ≥ 30 triệu USD; dữ liệu giảm phát được xác minh công khai | Quản trị hoàn toàn phi tập trung |

**Nguyên tắc thiết kế lộ trình:**

- **Kiểm toán trước TGE:** Token sẽ không bao giờ được phát hành nếu không hoàn thành kiểm tra bảo mật độc lập. Đây là sự đảm bảo cơ bản cho sự an toàn của tiền của người dùng.
- **Trình xác minh có trước người dùng:** Khi mạng chính trực tuyến, sẽ có ≥10 trình xác minh (dung sai lỗi BFT f ≥3), đảm bảo rằng mạng sẽ không bị ngừng hoạt động do một điểm lỗi duy nhất.
- **Đầu tư đi trước việc mở rộng:** Chỉ sau khi lần đầu tư đầu tiên thành công và tạo ra lợi nhuận có thể kiểm chứng được, chúng ta mới có thể tiến hành mở rộng quy mô lớn. Tránh đặt xe trước ngựa bằng cách “đi vòng người trước và tìm dự án sau”.
- **Bộ đệm thời gian:** Dự trữ bộ đệm thời gian 20-30% cho mỗi giai đoạn. Sự phát triển công nghệ, sửa chữa kiểm toán và quy trình pháp lý đều có thể vượt quá mong đợi và lộ trình không phải là "kịch bản lạc quan nhất".

**Mối quan hệ với Ngày phát hành Sách trắng (ngày 4 tháng 8 năm 2026):** Sách trắng được phát hành vào tháng 8 năm 2026 như một tuyên bố công khai về tầm nhìn và thiết kế kỹ thuật của dự án. Quá trình triển khai thực tế sẽ bắt đầu vào Quý 4 năm 2026 (giai đoạn chuẩn bị) và mục tiêu TGE là Quý 4 năm 2027. Khoảng cách khoảng 14 tháng giữa thời điểm phát hành sách trắng và TGE được sử dụng để thành lập nhóm, phát triển, kiểm tra và chuẩn bị tuân thủ.

---

## Chương 11: Văn hóa cộng đồng và Sinh thái nhà phát triển

### 11.1 Bốn giá trị

- **Minh bạch tốt hơn hoàn hảo** - Thà bộc lộ những điểm không hoàn hảo còn hơn là che giấu sự hoàn hảo. Tất cả các dòng ngân quỹ, quyết định đầu tư và phiếu bầu quản trị đều có sẵn vĩnh viễn trên chuỗi.
- **Dần dần tốt hơn triệt để** - Thực hiện các bước nhỏ và liên tục lặp lại. Khoản đầu tư đầu tiên sẽ bắt đầu từ 2-5 triệu USD và quy mô sẽ được mở rộng sau khi xác minh mô hình.
- **Trách nhiệm cao hơn quyền** - Quyền và nghĩa vụ ngang nhau. Các thành viên của ủy ban quản trị phải cam kết 50.000 LIGHT và tiết lộ chương trình chính sách của họ. Nếu họ không thực hiện nhiệm vụ của mình thì sẽ bị phạt.
- **Đa dạng tốt hơn đồng nhất** - Tiếng nói khác nhau là khả năng miễn nhiễm của hệ thống. Biểu quyết hai chiều (đồng xu + địa chỉ) đảm bảo rằng cả cá voi và nhà đầu tư bán lẻ đều có tiếng nói.

### 11.2 Hệ thống bồi thẩm đoàn

| Kích thước | Nội quy |
|------|------|
| Thành phần | Chọn ngẫu nhiên 12 người dùng nắm giữ ≥10.000 ĐÈN và không có hồ sơ vi phạm |
| Kỳ hạn | 30 ngày, sẽ được rút ngẫu nhiên lại sau khi hết hạn |
| Trách nhiệm | Nghe khiếu nại về hình phạt chống gian lận, cáo buộc gian lận đề xuất và tranh chấp cộng đồng |
| Quy trình | Người dùng bị trừng phạt có thể gửi bằng chứng trong vòng 72 giờ; bồi thẩm đoàn phải đưa ra phán quyết trong vòng 48 giờ |
| Tiêu chuẩn phán đoán | ≥8 trên 12 người (2/3 đa số) phải đồng ý giữ nguyên hoặc hủy bỏ hình phạt |
| Tránh né | Tự động thay thế bồi thẩm đoàn có quan hệ mời với các bên hoặc có cùng dải IP |
| Thù lao | Nhận trợ cấp dịch vụ bồi thẩm đoàn hàng ngày trị giá 5 LIGHT trong thời hạn (giải ngân từ quỹ sinh thái) |

### 11.3 Kế hoạch sinh thái dành cho nhà phát triển

| Mô-đun | Nội dung | Nguồn tài trợ | Cách đăng ký |
|------|------|----------|----------|
| Tài trợ cho nhà phát triển (Tài trợ) | Đối với các nhóm xây dựng dApp, công cụ và cơ sở hạ tầng trên chuỗi LightDAO, một khoản tài trợ duy nhất trị giá 5-500.000 USD tương đương với LIGHT | Quỹ phát triển sinh thái (Giai đoạn phát hành tuyến tính 2) | Gửi đề xuất → Đánh giá của cán bộ đánh giá kỹ thuật → Biểu quyết quản trị (quy trình đề xuất vi mô) |
| SDK và API | Cung cấp giao diện JavaScript/TypeScript SDK, REST API và WebSocket để hạ thấp ngưỡng phát triển của bên thứ ba | Cán bộ đánh giá kỹ thuật lãnh đạo phát triển | Mã nguồn mở, công khai trên GitHub |
| Hackathon | Một cuộc thi hackathon trực tuyến được tổ chức hàng quý với tổng giải thưởng 100.000 USD tương đương với LIGHT | Quỹ phát triển sinh thái | Đăng ký mở, không có ngưỡng |
| Tiền thưởng lỗi | Chương trình thưởng lỗi hợp đồng cốt lõi, thưởng $1.000-$50.000 cho một lỗ hổng hợp lệ duy nhất (được phân loại theo mức độ nghiêm trọng) | Quỹ bảo hiểm + Quỹ phát triển sinh thái | Gửi qua Immunefi hoặc nền tảng tự xây dựng |
| Thị trường hợp đồng CosmWasm | Khuyến khích các bên thứ ba triển khai hợp đồng thông minh và 20% thu nhập từ phí gas sẽ được trả lại vào kho bạc sinh thái để hỗ trợ các nhà phát triển | Phân phối phí gas (xem Phần 4.5) | Tự động, không cần ứng dụng |

### 11.4 Chiến lược đa ngôn ngữ và bản địa hóa

| Kích thước | Lập kế hoạch |
|------|------|
| Ngôn ngữ nền tảng | Ban đầu hỗ trợ tiếng Anh, tiếng Trung, tiếng Tây Ban Nha, tiếng Bồ Đào Nha và tiếng Philipin; Tiếng Pháp, tiếng Ả Rập, tiếng Swahili và tiếng Indonesia sẽ được thêm vào từ tháng thứ 6 |
| Ngôn ngữ quản trị | Các đề xuất và nền tảng chiến dịch được chấp nhận bằng bất kỳ ngôn ngữ nào và hệ thống cung cấp bản dịch máy + hiệu đính thủ công cho cộng đồng |
| Hoạt động cộng đồng | Thiết lập các kênh cộng đồng độc lập (Discord/Telegram) theo ngôn ngữ và mỗi kênh đều được trang bị các tình nguyện viên liên lạc cộng đồng tại địa phương |
| Dịch tài liệu | Sách trắng và tài liệu cốt lõi được hoàn thành bởi các tình nguyện viên dịch thuật cộng đồng và đóng góp dịch thuật được bao gồm trong phần thưởng hành vi "Đóng góp nội dung" (5%) |
| Tài trợ nội địa hóa | 10% (40 triệu xu) của quỹ phát triển sinh thái được dành cho việc khuyến khích xây dựng cộng đồng bản địa hóa và dịch thuật |

---

## Chương 12: Đội ngũ và nhà tư vấn

### 12.1 Định nghĩa vai trò cốt lõi

| Vai trò | Trách nhiệm | Yêu cầu về lý lịch | Phương pháp tiết lộ |
|------|------|----------|----------|
| Người giám hộ ban đầu/Nhà tài trợ dự án | Triển khai các hợp đồng ban đầu, lưu giữ tài liệu và điều phối các hoạt động ban đầu | ≥ 3 năm kinh nghiệm trong ngành blockchain, có hồ sơ triển khai hợp đồng thông minh hoặc giao thức DeFi | Tiết lộ danh tính thực sự của bạn trước TGE hoặc cung cấp báo cáo xác minh danh tính của bên thứ ba (chẳng hạn như chữ ký công chứng + xác minh tin nhắn trên chuỗi) |
| Trưởng nhóm kỹ thuật | Thiết kế kiến ​​trúc hợp đồng, quản lý nhóm phát triển, kiểm tra lắp ghép | Kinh nghiệm phát triển Cosmos SDK/CosmWasm, hồ sơ triển khai chuỗi sản xuất | Tương tự như trên |
| Người phụ trách đầu tư | Sàng lọc mục tiêu, phối hợp thẩm định, thành lập SPV, quản lý xuất cảnh | Kinh nghiệm trong ngành vốn cổ phần tư nhân/đầu tư mạo hiểm, với các trường hợp rút lui đã hoàn thành | Tương tự như trên |
| Tư vấn tuân thủ | Thiết kế cấu trúc pháp lý, kết nối quy định, tư vấn tuân thủ MLM | Luật sư có bằng cấp của Hoa Kỳ/EU/Cayman | Tên công ty luật công (tên cá nhân sẽ không được tiết lộ trừ khi tôi đồng ý) |

### 12.2 Ban cố vấn

- Bao gồm 3-5 chuyên gia tư vấn độc lập, bao gồm: Công nghệ DePIN, tuân thủ đầu tư xuyên biên giới, hoạt động cộng đồng và ngành tiêu dùng;
- Tư vấn viên nhận thù lao tư vấn dưới dạng token LIGHT (được giải ngân từ phần “dịch vụ đổi lấy token” của quỹ điều hành chiến lược) và bị khóa trong 12 tháng;
- Danh sách các chuyên gia tư vấn được công khai trước TGE và được mở để cộng đồng lấy ý kiến ​​(cuộc họp hỏi đáp bằng văn bản phi tập trung, xem Mục 7.5);
- Cố vấn không được đồng thời là thành viên của Ủy ban Quản trị (xung đột phân biệt lợi ích).

### 12.3 Cam kết và ràng buộc của nhóm

| Hạn chế | Nội quy |
|------|------|
| Khóa mã thông báo | LIGHT (bao gồm phân bổ quỹ điều hành chiến lược) do nhóm nòng cốt nắm giữ phải bị khóa trong 12 tháng và được phát hành tuyến tính trong 36 tháng sau khi mở khóa |
| Hạn chế bán hàng | Người giám hộ ban đầu không được phép bán ÁNH SÁNG thu được thông qua bất kỳ kênh nào (bao gồm airdrop, phần thưởng và tiền bồi thường) trong thời hạn giữ chức vụ (<24 tháng) |
| Xung đột lợi ích | Xung đột lợi ích của các thành viên trong nhóm phải được tiết lộ đầy đủ tại thời điểm bổ nhiệm (cho dù họ có nắm giữ các token DAO khác hay không, liệu chúng có liên quan đến các mục tiêu đầu tư tiềm năng hay không) |
| Hậu quả của việc không tiết lộ | Sau khi xác minh được việc không tiết lộ xung đột lợi ích, bạn sẽ bị cấm vĩnh viễn tham gia quản trị và 50% số token đã mở khóa sẽ bị tịch thu vào quỹ bảo hiểm |
| Cơ chế thay thế | Khi vai trò cốt lõi rời đi hoặc mất năng lực, ủy ban quản trị (người giám hộ ban đầu + người giám hộ thay thế trước khi thành lập) sẽ chỉ định người kế nhiệm, người này phải được cộng đồng công bố công khai trong 72 giờ mà không bị phản đối |

### 12.4 Bồi thường cho người đóng góp cốt lõi (20% quỹ hoạt động chiến lược)

- Tổng số lượng: 50 triệu ĐÈN (chiếm 2% tổng số lượng)
- Số người được bảo hiểm: 3-5 người
- Quy tắc phát hành: vách đá tháng 12 + tuyến tính 36 tháng (nghĩa là khoảng 1,157 triệu xu sẽ được phát hành mỗi tháng bắt đầu từ tháng thứ 13)
- Mốc ràng buộc: Hàng quý, Ban quản trị (người giám hộ ban đầu + bên thứ ba độc lập trước khi thành lập) xác nhận đã đạt mốc trước khi giải phóng chỉ tiêu quý.
- Quy tắc tiết lộ: chỉ tiết lộ tổng số tiền và quy tắc phát hành, không tiết lộ tên cá nhân và hạn ngạch một người (để bảo vệ quyền riêng tư, đồng thời, tổng số tiền có thể được xác minh thông qua địa chỉ nhiều chữ ký trên chuỗi mà tổng số tiền không vượt quá)

---

## Chương 13: Cảnh báo rủi ro và tuyên bố từ chối trách nhiệm

### 13.1 Cảnh báo rủi ro

| Loại rủi ro | Mô tả | Biện pháp giảm thiểu |
|----------|------|---------|
| Rủi ro thị trường | Giá LIGHT có thể dao động đáng kể và giá lịch sử không thể hiện hiệu suất trong tương lai. TGE có thanh khoản ban đầu hạn chế và giá có thể biến động dữ dội | Đấu giá kiểu Hà Lan định giá hợp lý; Bộ ngắt mạch ±50% 72 giờ sau TGE; cơ chế can thiệp bốn cấp xoắn ốc chống tử vong |
| Rủi ro dự án | Mục tiêu đầu tư có thể bị thua lỗ, dự án đầu tư mạo hiểm có thể thất bại và toàn bộ số tiền gốc có thể bị mất. Tỷ lệ thất bại trung bình trong lịch sử của ngành PE/VC là khoảng 50-70% (thỏa thuận đơn lẻ) | Phân cấp động cơ kép (70% dòng tiền + tăng trưởng 30%); mục tiêu duy nhất 25%; công nghiệp ≤ 40%; vùng 30%; dự phòng 10% cho quỹ bảo hiểm |
| Rủi ro kỹ thuật | Hợp đồng thông minh có thể có những lỗ hổng chưa được phát hiện; khả năng tương thích của trình duyệt có thể ảnh hưởng đến trải nghiệm khai thác; cầu nối chuỗi có thể bị tấn công | Kiểm toán độc lập + xác minh chính thức trước TGE; Tiền thưởng lỗi $1K-$50K; khóa thời gian 72 giờ; cơ chế treo đa chữ ký |
| Rủi ro pháp lý | Chính sách quy định ở nhiều quốc gia và khu vực khác nhau có thể thay đổi, điều này có thể dẫn đến hạn chế về chức năng hoặc người dùng ở các khu vực cụ thể không thể tham gia | Cấu trúc SPV của Cayman; xác minh bằng 0 mặc định (việc xác minh được thực hiện bởi bên thứ ba được cấp phép về phía dịch vụ của họ); gương IPFS mặt trước có khả năng chống kiểm duyệt; không được tiếp thị cho các quốc gia cụ thể |
| Rủi ro thanh khoản | Mã thông báo phụ có thể thiếu độ sâu giao dịch đủ trong giai đoạn đầu; LIGHT có thể phải đối mặt với áp lực bán trong giai đoạn đầu của TGE | Tính thanh khoản ban đầu của mã thông báo phụ AMM (6% số lượng phát hành); Thời gian khóa chuyển khoản 30 ngày; Nhóm/nhà đầu tư Vách đá 12 tháng + tuyến tính 36 tháng |
| Rủi ro pha loãng | Khi số lượng người khai thác đang hoạt động tăng lên, doanh thu khai thác bình quân đầu người đương nhiên sẽ bị giảm đi (mẫu số BaseReward tăng) | Mục đích thiết kế: những người tham gia sớm chấp nhận rủi ro cao hơn để thu được lợi nhuận cao hơn; người dùng sau này có thể tăng tốc tích lũy thông qua chia sẻ lời mời; ngưỡng quản trị được hạ xuống một cách linh hoạt |
| Rủi ro hoạt động | Hoạt động và quản lý của công ty được đầu tư có thể không đáp ứng được kỳ vọng; Hoạt động của SPV dựa vào giám đốc bên thứ ba; đội đầu tư có thể bị thua | Điều lệ SPV hạn chế + giám đốc độc lập; DAO có thể bỏ phiếu để thay thế giám đốc; điều khoản trọng tài SIAC/ICC; bảo hiểm người chủ chốt (đang thăm dò) |
| Rủi ro cầu nối chuỗi | Cầu chuỗi chéo wLIGHT được vận hành bởi một bên thứ ba và các lỗ hổng hợp đồng cầu nối có thể dẫn đến tổn thất tài sản (lịch sử, cầu chuỗi chéo là nguồn tổn thất lớn nhất) | Kiểm toán độc lập trước khi cầu đi vào hoạt động; tài sản cầu không vượt quá 5% tổng nguồn cung; tiết lộ rủi ro; người dùng có thể chọn chỉ sử dụng chuỗi gốc |
| Rủi ro xác nhận | Những người xác thực cùng nhau ngoại tuyến hoặc phạm tội ác có thể khiến chuỗi tạm dừng sản xuất khối và tất cả các hoạt động của người dùng (khai thác, bỏ phiếu, chuyển giao) tạm thời không khả dụng | Tendermint BFT dung túng <1/3 cái ác; người xác nhận ≥ 21 (f=6); Hình phạt chém; cơ chế bỏ phiếu di cư khẩn cấp |

### 13.2 Tuyên bố miễn trừ trách nhiệm

- LIGHT và token phụ không phải là chứng khoán, không có giá trị nội tại và giá có thể trở về 0. Sách trắng này không phải là bất kỳ hình thức tài liệu phát hành chứng khoán, đề nghị đầu tư hoặc tư vấn đầu tư nào.
- Việc phân phối thu nhập của thỏa thuận phụ thuộc vào hiệu quả hoạt động thực tế của tài sản cơ bản và dữ liệu lịch sử không thể hiện thu nhập trong tương lai. Bất kỳ mô tả nào về lợi nhuận đầu tư đều là ước tính hướng tới tương lai và không phải là lời hứa hẹn.
- Người dùng phải chịu mọi tổn thất do mất hoặc rò rỉ khóa riêng và thỏa thuận không cung cấp dịch vụ truy xuất. Sử dụng ví Cấp 1 (Mật mã) hoặc Cấp 2 (Phục hồi xã hội) sẽ giảm rủi ro này nhưng không loại bỏ được nó.
- Thỏa thuận này dành cho người dùng trên toàn thế giới (tuân theo luật pháp và quy định hiện hành). Người dùng nên xác nhận thái độ pháp lý đối với tài sản được mã hóa, tổ chức DAO và chứng chỉ thu nhập SPV trong khu vực pháp lý của họ và đảm bảo rằng sự tham gia của họ là hợp pháp và tuân thủ.
- Các tuyên bố hướng tới tương lai trong sách trắng này (bao gồm lộ trình, mô hình doanh thu, ước tính giảm phát, dự báo quy mô đầu tư) là những dự đoán dựa trên các giả định hiện tại và kết quả thực tế có thể sai lệch đáng kể do thị trường, công nghệ, quy định, hoạt động của nhóm và các yếu tố khác.
- Khuyến khích mời chào là cơ chế chia sẻ một cấp và không cấu thành các mô hình tiếp thị đa cấp hoặc kim tự tháp. Tuy nhiên, người dùng vẫn nên xác nhận thái độ pháp lý đối với phần thưởng giới thiệu trong khu vực pháp lý của họ.
- Độ tuổi tối thiểu để tham gia vào hệ sinh thái LightDAO là 18 tuổi (hoặc độ tuổi trưởng thành hợp pháp tại khu vực pháp lý của bạn, tùy theo độ tuổi nào cao hơn). Trẻ vị thành niên không được phép tham gia khai thác, quản trị hoặc đầu tư.

---

## Phụ lục A: Bảng tóm tắt các thông số chính

| Danh mục | Tham số | Giá trị |
|------|------|------|
| Phát hành | Tổng số tiền | 2,5 tỷ đồng, không bao giờ phát hành thêm |
| Phát hành | Khai thác | 40% = 1 tỷ xu |
| Phát hành | Kho đầu tư | 34% = 850 triệu xu |
| Phát hành | Quỹ sinh thái | 16% = 400 triệu chiếc |
| Phát hành | Hoạt động chiến lược | 10% = 250 triệu xu (dịch vụ 50%/tài chính 30%/người đóng góp 20%) |
| Phát hành | Chu kỳ giảm một nửa | 2 năm một lần |
| Phát hành | Ngày phát hành kỷ nguyên đầu tiên | ≈684.900 (thợ đào 95% = 650.700, người xác thực 5% = 34.200) |
| Phát hành | Nhóm phần thưởng mỗi khối | ≈13,87 ÁNH SÁNG |
| Khai thác | Trọng lượng đóng góp | Băng thông 40%/phiên 30%/xác minh 20%/độ ổn định 10% |
| Khai thác | Tiền thưởng đầy đủ | 1,44 lần |
| Lời mời | Nhà truyền giáo/Đại sứ/Đối tác | 3 người 10%+100L/10 người 15%+500L+5%/50 người 20%+2500L+10% |
| Hành vi | Bốn mặt hàng × 5% | Giới hạn trên 20% |
| Phí xăng | Cơ chế định giá | Neo tương đương USD, được oracle tự động chuyển đổi thành số lượng LIGHT sau mỗi 24 giờ |
| Phí xăng | Chuyển khoản thông thường | Tương đương 0,001 USD (@$0,05=0,02 LIGHT) |
| Phí xăng | Biểu quyết quản trị | Tương đương 0,005 USD (@$0,05=0,10 LIGHT) |
| Phí xăng | Quy tắc phân phối | Phá hủy 50% / 30% người xác nhận / 20% kho bạc sinh thái |
| Giảm phát | Suy thoái/cảnh báo sớm/điểm mấu chốt | 1,5 tỷ/ 1,2 tỷ/ 1 tỷ (khối lượng phát hành) |
| Giảm phát | Giới hạn trên lý thuyết | 1,65 tỷ (10+4+2,5, 850 triệu trong kho bạc sẽ không bao giờ được lưu hành) |
| Quản trị | Ngưỡng đề xuất | ≥5.000 LIGHT + 30 ngày đặt cọc |
| Quản trị | Ủy ban đặt cược | 50.000 ÁNH SÁNG + 100 Địa chỉ |
| QUẢN TRỊ | BỒI THẦU | 10.000 ÁNH SÁNG |
| Quản trị | Cá cược | 5—500 ÁNH SÁNG |
| Quản trị | Tiền thưởng danh tiếng | 1 năm +15 phiếu bầu → +30% (tổng giới hạn +40%) |
| Đầu tư | Giới hạn đơn | Vault còn lại × 15% (127,5 triệu xu ban đầu) |
| Đầu tư | Đường cơ sở có thể triển khai | 850 triệu × 0,15 USD × 75% = 95,63 triệu USD ≈ 100 triệu USD |
| Đầu tư | Phân phối lợi nhuận (hàng năm) | 30/40/20/10 |
| Đầu tư | Phân phối lợi nhuận (thoát) | 70/30 |
| Đấu giá | Mục tiêu | 15 triệu USD (dự trữ 5 triệu USD + vốn đầu tư 10 triệu USD) |
| Dự trữ | Kho bạc ổn định | TGE 5 triệu USD → Tháng 24 8 triệu USD |
| Bảo hiểm | Lợi nhuận | Lợi nhuận 10% |
| Thả rơi | Tổng ngân sách | 55 triệu (quỹ sinh thái 13,75%), CAC≈$55/người dùng giữ lại |
| Trình xác nhận | Ban đầu/Giới hạn | 21 (tối thiểu 10) / 100 |
| Trình xác thực | cổ phần tối thiểu | 500.000 ĐÈN |
| Người xác minh | Điểm mấu chốt của TGE | ≥7, nếu không sẽ không được phép lên mạng |

---

## Phụ lục B: Đạo hàm và kiểm chứng số

### B.1 Sản lượng khai thác

2A=1 tỷ→A=500 triệu. Phát hành hàng ngày = 500 triệu 730 = 684.932 ≈ 684.900. Nhóm khai thác=684.932×95%=650.685≈650.700. Người xác minh=684.932×5%=34.247≈34.200. Mỗi khối=684.932->49.371≈13,87. Xác thực: 684.932×730=499.999.960≈500 triệu ✓

### B.2 Khả năng tiếp cận ngưỡng quản trị

Điểm chuẩn 100.000 thợ mỏ (6,51/ngày, đối tác 74,44/ngày): đề xuất 5.000→768 ngày/67 ngày; ủy ban 50.000→7.684 ngày (21 năm)/672 ngày (22 tháng); bồi thẩm đoàn 10.000→1.537 ngày (4,2 năm)/134 ngày (4,5 tháng); đặt cược 500→77 ngày/6,7 ngày.

Giai đoạn hạt giống (10.000 thợ mỏ, 65,07/ngày, đối tác 744,4/ngày): đề xuất → 77 ngày (2,5 tháng) / 6,7 ngày; ủy ban → 768 ngày (25 tháng) / 67 ngày (2,2 tháng); bồi thẩm đoàn → 154 ngày (5 tháng) / 13,4 ngày.

### B.3 Mốc thời gian giảm phát

Khối lượng lưu thông = khai thác + sinh thái + chiến lược (được giao) - trao đổi - Gas - mua lại. 850 triệu trong kho bạc sẽ không bao giờ được lưu hành.

| Năm | Khai thác tích lũy | Sinh thái | Chiến lược | Trao đổi | Khí | Mua lại | Lưu thông |
|------|--------|------|------|------|------|------|--------|
| 1 | 2,50 | 2,80 | 0 | 0 | 0,01 | 0 | ≈5,29 |
| 2 | 5 giờ 00 | 4 giờ 00 | 0,83 | 0,05 | 0,02 | 0 | ≈9,76 |
| 3 | 6,25 | 4 giờ 00 | 1,67 | 0,20 | 0,03 | 0,05 | ≈11,64 |
| 4 | 7h50 | 4 giờ 00 | 2,50 | 0,45 | 0,04 | 0,20 | ≈13.31(cao điểm) |
| 5 | 8.13 | 4 giờ 00 | 2,50 | 0,80 | 0,05 | 0,50 | ≈13,28 |
| 6 | 8,75 | 4 giờ 00 | 2,50 | 1,20 | 0,06 | 0,90 | ≈13.09 |
| 7 | 9.06 | 4 giờ 00 | 2,50 | 1,60 | 0,07 | 1,40 | ≈12,49 |
| 8 | 9,38 | 4 giờ 00 | 2,50 | 2,00 | 0,08 | 1,90 | ≈11,89 |
| 9 | 9,53 | 4 giờ 00 | 2,50 | 2,40 | 0,09 | 2h30 | ≈11,24 |
| 10 | 9,69 | 4 giờ 00 | 2,50 | 2,80 | 0,10 | 2,70 | ≈10,59 |
| 11 | 9,77 | 4 giờ 00 | 2,50 | 3.10 | 0,11 | 3,00 | ≈10.06 |
| 12 | 9,84 | 4 giờ 00 | 2,50 | 3,40 | 0,12 | 3h30 | ≈9,52 |

Kết luận: Đỉnh Y4≈1,331 tỷ đồng; Y8 chạm ngưỡng cảnh báo 1,2 tỷ; Y11-12 chạm mốc 1 tỷ; Đường giảm tốc 1,5 tỷ chỉ là kịch bản hủy diệt cực thấp.

---

## Phụ lục C: Nhật ký sửa lỗi kiểm tra (tổng cộng 36 mục)

Gồm 22 hạng mục gốc (L1-5, A1-4, D1-4, M1-8, G1-3) + 7 hạng mục kiến ​​trúc kỹ thuật (T1-7) + 7 hạng mục tối ưu hóa mô hình kinh tế trong vòng này:

| Số | Sửa chữa |
|------|------|
| E-1 | Tổng số tiền 2,1 tỷ → 2,5 tỷ (do hạn chế về năng lực đầu tư) |
| E-2 | Phân bổ 50/30/20→40/34/16/10 (10% quỹ hoạt động chiến lược mới) |
| E-3 | Đấu giá Hà Lan 10 triệu USD→15 triệu USD (vốn đầu tư ban đầu 5 triệu USD→10 triệu USD) |
| E-4 | Kế hoạch tăng trưởng airdrop 5,7 phần mới (55 triệu chiếc, CAC $55/người) |
| E-5 | Trình xác minh được triển khai theo từng giai đoạn (Testnet 7→TGE tối thiểu 10/Mục tiêu 21→Mở 100) |
| E-6 | Điều chỉnh đường kích hoạt giảm phát (14/12/10 → 15/12/10, thích ứng với giới hạn lưu thông 1,65 tỷ) |
| E-7 | Thay thế tất cả các trích dẫn bên ngoài bằng các nguồn có thể kiểm chứng được (xóa các bài viết SSRN không thể kiểm chứng được) |

---

## Phụ lục D: Mục lục nhanh các thuật ngữ

Giải thích đầy đủ về mỗi thuật ngữ được ghi chú trong khối nhận xét [Điều khoản trong Chương này] ở cuối chương nơi nó xuất hiện lần đầu. Chỉ mục này liệt kê tất cả các thuật ngữ và chương của chúng theo thứ tự bảng chữ cái để điều hướng nhanh chóng.

| Thuật ngữ | Chương định nghĩa |
|------|-------------|
| AMM (Nhà tạo lập thị trường tự động) | Chương 4 |
| BFT (Khả năng chịu lỗi Byzantine) | Chương 4 |
| CAC (Chi phí thu hút khách hàng) | Chương 5 |
| CEX (Sàn giao dịch tập trung) | Chương 4 |
| SDK vũ trụ | Chương 4 |
| Vũ trụWasm | Chương 4 |
| DAO (Tổ chức tự trị phi tập trung) | Chương 2 |
| DCF (Phương pháp dòng tiền chiết khấu) | Chương 9 |
| DePIN (Mạng cơ sở hạ tầng vật lý phi tập trung) | Chương 2 |
| DEX (Sàn giao dịch phi tập trung) | Chương 4 |
| EBITDA (thu nhập trước lãi vay, thuế, khấu hao và khấu hao) | Chương 9 |
| Phí gas | Chương 4 |
| IBC (Giao thức truyền thông liên chuỗi) | Chương 3 |
| IPFS (Hệ thống tệp liên hành tinh) | Chương 4 |
| KYC (Biết khách hàng của bạn) | Chương 3 |
| ÁNH SÁNG (mã thông báo gốc) | Chương 4 |
| LP (Nhà cung cấp thanh khoản) | Chương 5 |
| PE Thị trường Trung bình Hạ (Vốn cổ phần tư nhân Thị trường Trung bình Hạ nguồn) | Chương 2 |
| Cây Merkle | Chương 4 |
| MiFID II (Chỉ thị về công cụ tài chính của thị trường EU II) | Chương 3 |
| MLM (Tiếp thị đa cấp) | Chương 3 |
| PII (Thông tin nhận dạng cá nhân) | Chương 3 |
| PoC (Bằng chứng đóng góp) | Chương 4 |
| PoS (Bằng chứng cổ phần) | Chương 4 |
| PoW (Bằng chứng công việc) | Chương 4 |
| Trước IPO | Chương 9 |
| PWA (Ứng dụng web lũy tiến) | Chương 4 |
| Reg D/Reg S (Quy định D/S của Đạo luật Chứng khoán Hoa Kỳ) | Chương 3 |
| Chém | Chương 4 |
| SPV (Xe chuyên dụng) | Chương 2 |
| TGE (Sự kiện tạo mã thông báo) | Chương 5 |
| TWAP (Giá trung bình có trọng số theo thời gian) | Chương 4 |
| Thực thi TWAP (Lệnh mua lại và chia nhỏ) | Chương 9 |
| VWAP (Giá trung bình theo khối lượng) | Chương 5 |
| wLIGHT (LIGHT đóng gói) | Chương 5 |
| ZK-KYC (KYC không có kiến ​​thức) | Chương 3 |
| Mã thông báo phụ | Chương 5 |
| Vòng xoáy tử thần | Chương 5 |
| Giảm một nửa | Chương 5 |
| Kho bạc (Kho bạc) | Chương 5 |
| Đấu giá Hà Lan | Chương 5 |
| Oracle | Chương 4 |

---

**Kết thúc toàn bộ giấy trắng**

**Tuyên bố về bản quyền:** Tài liệu này là tài liệu cộng đồng nguồn mở và có thể được sao chép tự do nhưng phải giữ lại nội dung đầy đủ.

---

# Phụ lục: Các tham số và địa chỉ được xác minh của Mainnet (V2.4 trực tiếp)

## A. §4.5 Thông số đo lường kinh tế khí đốt
- công thức giá gas tối thiểu: `(TransferUsdTarget / UsdPerLight) × 10^6 / RefTransferGas`; TransferUsdTarget hiện tại=$0,001, UsdPerLight=$0,05, RefTransferGas=100000 → **0,2 ulight/gas**
- Đo lường phân phối (tổng phí 300000 ulight): phá hủy 150000 (50%)/kho bạc 60000(20%)/người xác minh 90000(30%), khớp chính xác
- Địa chỉ hủy: `wasm1aeaty43lrlt9rmkyxujkkfuddnsfye6az4htcu` (địa chỉ chết xác định)
- Kho bạc: hợp đồng `kho bạc_multisig` (3/5 đa chữ ký; truy vấn `người ký` trên chuỗi trả về 5 người ký, bản thân ngưỡng không có trong giao diện truy vấn)

## B. Địa chỉ hợp đồng cốt lõi
Xem kho lưu trữ `docs/MAINNET_STATUS.md` (light_token / mining_reward / quản trị / kho bạc_multisig / oracle_twap / vesting và 10 hợp đồng khác).

## C. Xử lý mệnh giá (cổ phần) kế thừa
Genesis không khớp mint_denom=cổ phần đã được đặt lại về 0 và việc phát hành bổ sung đã dừng lại; cổ phần hiện có (khoảng 2,56e11 đơn vị vi mô) bị bỏ lại không có mục đích và kế hoạch xử lý (trao đổi/hủy bỏ) đang chờ đề xuất quản trị và sẽ không ảnh hưởng đến mô hình kinh tế ulight.

## D. §4.4 trao quyền trực tiếp
Vault 250.000.000 LIGHT, 3 lịch trình độc lập: 75M (vách đá 0)/ 100M (vách đá 1 năm)/ 75M (vách đá 2 năm), đã có trên chuỗi.

## E. Thực hành an toàn
- Mạng chính được nâng cấp lên x/nâng cấp quản trị + khả năng phối hợp cao của tất cả các nút trong cùng một khối + cơ quan giám sát tự động hoán đổi, được thực thi sau buổi diễn tập end-to-end của mạng thử nghiệm
- Hạt mật mã chỉ lưu trữ bản mã; Các mảnh Shamir không lưu trữ chúng cục bộ.
- Ngưỡng gửi root khai thác hợp đồng 5 (ngưỡng đo thực tế=5 cho mỗi sự kiện `submit_root` trên chuỗi; hiện có 5 tài khoản được ủy quyền đang ký và 7 ghế là mục tiêu thiết kế); để chống phù thủy/chống gian lận, xem §4.8
