#ifndef RPMGAUGE_H
#define RPMGAUGE_H

#include <QWidget>
#include <QTimer>

class RpmGauge : public QWidget
{
    Q_OBJECT

public:
    explicit RpmGauge(QWidget *parent = nullptr);
    ~RpmGauge() override = default;

    void setRpm(int rpm);

protected:
    void paintEvent(QPaintEvent *event) override;

private slots:
    void simulateEngine();

private:
    int m_rpm;
    int m_maxRpm;
    int m_redlineRpm;
    int m_targetRpm;
    int m_gear;
    bool m_revvingUp;

    QTimer *m_simTimer;
};

#endif // RPMGAUGE_H
