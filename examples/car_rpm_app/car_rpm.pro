QT += core gui widgets

TARGET = car_rpm
TEMPLATE = app

CONFIG += static release

SOURCES += \
    main.cpp \
    rpmgauge.cpp

HEADERS += \
    rpmgauge.h
