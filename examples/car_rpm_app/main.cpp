#include <QApplication>
#include "rpmgauge.h"

int main(int argc, char *argv[])
{
    // Point directly to the SPI display framebuffer if not set externally
    if (qEnvironmentVariableIsEmpty("QT_QPA_PLATFORM")) {
        qputenv("QT_QPA_PLATFORM", "linuxfb:fb=/dev/fb1");
    }

    QApplication a(argc, argv);
    a.setOverrideCursor(Qt::BlankCursor);

    RpmGauge gauge;
    gauge.resize(480, 320);
    gauge.showFullScreen();

    return a.exec();
}
