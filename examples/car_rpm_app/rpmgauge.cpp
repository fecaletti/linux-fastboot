#include "rpmgauge.h"
#include <QPainter>
#include <QPaintEvent>
#include <cmath>

RpmGauge::RpmGauge(QWidget *parent)
    : QWidget(parent)
    , m_rpm(800)
    , m_maxRpm(8000)
    , m_redlineRpm(6500)
    , m_targetRpm(4500)
    , m_gear(1)
    , m_revvingUp(true)
{
    setAttribute(Qt::WA_OpaquePaintEvent);
    setAttribute(Qt::WA_NoSystemBackground);

    // Simulation timer at ~30 FPS (33ms) - optimal for Pi Zero W CPU & SPI bus
    m_simTimer = new QTimer(this);
    connect(m_simTimer, &QTimer::timeout, this, &RpmGauge::simulateEngine);
    m_simTimer->start(33);
}

void RpmGauge::setRpm(int rpm)
{
    m_rpm = qBound(0, rpm, m_maxRpm);
    update();
}

void RpmGauge::simulateEngine()
{
    // Simple revving & shifting simulation
    if (m_revvingUp) {
        m_rpm += 120 + (m_gear * 20);
        if (m_rpm >= m_targetRpm) {
            if (m_gear < 5 && m_rpm >= 6200) {
                m_gear++;
                m_rpm -= 2200; // Gear shift drop
                m_targetRpm = (m_gear == 5) ? 7200 : 6600;
            } else if (m_gear >= 5 && m_rpm >= 7400) {
                m_revvingUp = false;
            }
        }
    } else {
        m_rpm -= 90;
        if (m_rpm <= 1000) {
            m_rpm = 900;
            m_gear = 1;
            m_targetRpm = 6400;
            m_revvingUp = true;
        }
    }
    update();
}

void RpmGauge::paintEvent(QPaintEvent * /*event*/)
{
    QPainter p(this);
    p.setRenderHint(QPainter::Antialiasing);

    // Dark background
    p.fillRect(rect(), QColor(14, 17, 23));

    int side = qMin(width(), height());
    int cx = width() / 2;
    int cy = height() / 2 + 20;
    int radius = (side / 2) - 25;

    // Angle range: 225 deg (bottom-left) down to -45 deg (bottom-right) = 270 total span
    const double startAngleDeg = 225.0;
    const double spanAngleDeg = 270.0;

    // 1. Draw outer gauge track
    QRectF trackRect(cx - radius, cy - radius, radius * 2, radius * 2);
    QPen trackPen(QColor(40, 48, 60), 10, Qt::SolidLine, Qt::RoundCap);
    p.setPen(trackPen);
    p.drawArc(trackRect, -45 * 16, spanAngleDeg * 16);

    // 2. Draw active RPM arc
    double currentFrac = static_cast<double>(m_rpm) / m_maxRpm;
    double activeSpan = spanAngleDeg * currentFrac;
    QColor arcColor = (m_rpm >= m_redlineRpm) ? QColor(239, 68, 68) : QColor(14, 165, 233);
    QPen activePen(arcColor, 10, Qt::SolidLine, Qt::RoundCap);
    p.setPen(activePen);
    // Qt drawArc angles: counter-clockwise, 3 o'clock is 0
    // Start angle in Qt convention is (225) * 16, with negative span for clockwise
    p.drawArc(trackRect, static_cast<int>((startAngleDeg) * 16), static_cast<int>(-activeSpan * 16));

    // 3. Draw tick marks and numbers (0 to 8 x1000)
    for (int i = 0; i <= 8; ++i) {
        double tickFrac = static_cast<double>(i * 1000) / m_maxRpm;
        double angleDeg = startAngleDeg - (tickFrac * spanAngleDeg);
        double angleRad = angleDeg * M_PI / 180.0;

        int x1 = cx + static_cast<int>((radius - 12) * std::cos(angleRad));
        int y1 = cy - static_cast<int>((radius - 12) * std::sin(angleRad));
        int x2 = cx + static_cast<int>((radius - 24) * std::cos(angleRad));
        int y2 = cy - static_cast<int>((radius - 24) * std::sin(angleRad));

        bool isRedline = (i * 1000 >= m_redlineRpm);
        p.setPen(QPen(isRedline ? QColor(239, 68, 68) : QColor(200, 210, 225), 2));
        p.drawLine(x1, y1, x2, y2);

        // Labels
        int tx = cx + static_cast<int>((radius - 38) * std::cos(angleRad));
        int ty = cy - static_cast<int>((radius - 38) * std::sin(angleRad));
        p.setFont(QFont("Monospace", 9, QFont::Bold));
        p.drawText(QRect(tx - 12, ty - 10, 24, 20), Qt::AlignCenter, QString::number(i));
    }

    // 4. Center digital readout
    p.setPen(QColor(240, 245, 255));
    p.setFont(QFont("Monospace", 28, QFont::Bold));
    p.drawText(QRect(cx - 100, cy - 35, 200, 40), Qt::AlignCenter, QString::number(m_rpm));

    p.setFont(QFont("Monospace", 10, QFont::Normal));
    p.setPen(QColor(148, 163, 184));
    p.drawText(QRect(cx - 100, cy + 5, 200, 20), Qt::AlignCenter, "RPM x1000");

    // Gear indicator
    p.setFont(QFont("Monospace", 14, QFont::Bold));
    p.setPen(QColor(56, 189, 248));
    p.drawText(QRect(cx - 40, cy + 30, 80, 24), Qt::AlignCenter, QString("GEAR %1").arg(m_gear));

    // Needle pointer
    double needleAngleDeg = startAngleDeg - (currentFrac * spanAngleDeg);
    double needleAngleRad = needleAngleDeg * M_PI / 180.0;
    int nx = cx + static_cast<int>((radius - 16) * std::cos(needleAngleRad));
    int ny = cy - static_cast<int>((radius - 16) * std::sin(needleAngleRad));
    p.setPen(QPen(arcColor, 3, Qt::SolidLine, Qt::RoundCap));
    p.drawLine(cx, cy, nx, ny);

    // Center hub cap
    p.setPen(Qt::NoPen);
    p.setBrush(QColor(220, 230, 245));
    p.drawEllipse(QPoint(cx, cy), 6, 6);
}
