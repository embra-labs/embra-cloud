# Embra · Mỗi lần deploy đều có đường lui

Hosting app cho developer và team nhỏ tại Việt Nam, tập trung vào ứng dụng có PostgreSQL. Embra đang xây dựng luồng deploy từ code đến app và database, với review migration và chuẩn bị phục hồi.

**Cập nhật 08/10/2026:** đang phát triển và nhận đăng ký quan tâm closed alpha. Ngày mở đợt thử chưa chốt; onboarding thủ công theo lời mời.

[Bắt đầu ở đây](https://github.com/embra-labs/.github/blob/main/docs/start-here.md) · [Engineering](https://embra.cloud/engineering/) · [Đăng ký quan tâm](https://embra.cloud/#join) · [Hỗ trợ](https://github.com/embra-labs/.github/blob/main/SUPPORT.md)

## Từ nền tảng đến trải nghiệm sản phẩm

**M1** xây nền tảng: CLI, app đóng gói thành container image, PostgreSQL và migration gate. Image được build bằng công cụ bên ngoài và ghim theo digest.

**M2** tiếp tục flow sản phẩm đang minh hoạ trên website: build, deploy, review và recovery. Giao diện, build từ source và MCP là hướng phát triển tiếp theo. Khả năng dùng thử thực tế được xác nhận trong lời mời, không suy từ phạm vi M1 hoặc màn hình demo.

Embra hướng tới frontend, Node.js / Next.js và PostgreSQL. File storage, worker, queue, auth, email và realtime là roadmap mở rộng.

## Có thể kiểm chứng ngay

| Nội dung | Phạm vi bằng chứng |
| :--- | :--- |
| [Backfill 8 triệu dòng](https://embra.cloud/engineering/backfill-8m/) | Lab 28–30/09/2026: toàn vẹn đạt trong fixture; mục tiêu latency chưa đạt |
| [backfill-demo](https://github.com/embra-labs/backfill-demo) | Fixture riêng 1.000 dòng, code + CI, kill trước/sau commit và đối chứng sai; không tái lập benchmark cũ |
| [Flow sản phẩm](https://embra.cloud/#stage) | Minh hoạ hướng tới M2; chưa phải giao diện phát hành, không chạy trên app thật |

Các thử nghiệm dùng dữ liệu tổng hợp. Số thời gian và chi phí trong minh hoạ là ví dụ. Restore về mốc cũ có thể bỏ các lần ghi sau mốc đó; kết quả lab không phải SLA hoặc cam kết phục hồi không mất dữ liệu.

## Hoàng Xuân / Founder

Mình từng phá hỏng database của công ty.

Khi xây Embra, mình luôn nghĩ về tình huống đó: app đang lỗi, mọi người chờ hệ thống hoạt động lại, còn người xử lý phải tìm xem dữ liệu nào đã mất, backup có dùng được không và restore sẽ mất bao lâu.

Với một team nhỏ, người viết code thường cũng là người deploy và xử lý sự cố. Bạn cần đưa tính năng mới lên, nhưng mỗi thay đổi database lại có thể ảnh hưởng tới dữ liệu đang chạy thật.

Đó là vấn đề mình muốn giải quyết với Embra: thấy rủi ro trước khi chạy migration, có bước review rõ ràng và chuẩn bị đường restore trước khi cần đến nó.

Embra đang được xây dựng theo hướng đó. Mình muốn cùng những team đầu tiên kiểm chứng nó trên project thử nghiệm.

Mình trực tiếp xây dựng và support. Embra hiện là dự án cá nhân, chưa có pháp nhân. [GitHub](https://github.com/hxuan190) · [LinkedIn](https://www.linkedin.com/in/hxuan190)

## Đăng ký quan tâm alpha

1. [Đăng ký quan tâm](https://embra.cloud/#join) và xác nhận email; bước này chưa cấp quyền truy cập.
2. Khi có đợt phù hợp, Embra liên hệ để xác nhận stack, giới hạn, chi phí và cách hỗ trợ.
3. Trước khi thử, bạn nhận hướng dẫn truy cập, phiên bản được hỗ trợ và cách lấy dữ liệu ra khi kết thúc.

Đăng ký không tạo tài nguyên hoặc phát sinh phí. CLI chưa có bản public; chưa nhận app production. Giá chưa chốt. Hạ tầng dự kiến tại TP.HCM, địa điểm chưa chốt; vị trí xử lý dữ liệu của từng dịch vụ và bên tích hợp được công bố theo phạm vi cung cấp.

[Changelog](https://github.com/embra-labs/.github/blob/main/docs/changelog.md) · [Hỗ trợ / báo lỗi](https://github.com/embra-labs/.github/blob/main/SUPPORT.md) · [hello@embra.cloud](mailto:hello@embra.cloud) · [Thông báo xử lý dữ liệu](https://embra.cloud/chinh-sach-du-lieu.html) · [Thông tin cho agent](https://embra.cloud/llms.txt)
