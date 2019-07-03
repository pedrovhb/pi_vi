# coding=utf-8
import logging
import time
import os
import sys

try:
    import linuxcnc
except ImportError:
    import mock_linuxcnc as linuxcnc

log = logging.getLogger('logica')
log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler(sys.stdout))
s = linuxcnc.stat()
c = linuxcnc.command()


class LogicaPI(object):

    def __init__(self):

        self.di_abb_bit0 = 8
        self.di_abb_bit1 = 9
        self.di_abb_bit2 = 10

        # hm2_5i25.0.7i77.0.0.output-07
        # net ABRE_MORSA <= motion.digital-out-05
        self.do_morsa_abre = 5

        # hm2_5i25.0.7i77.0.0.output-06
        # net FECHA_MORSA <= motion.digital-out-06
        self.do_morsa_fecha = 6

        # hm2_5i25.0.7i77.0.0.output-05
        # net INICIO_CICLO_ABB <= motion.digital-out-10
        self.do_inicio_ciclo_abb = 10

        # hm2_5i25.0.7i77.0.0.output-01
        # net VERIFICACAO_OK <= motion.digital-out-11
        self.do_verificacao_ok = 11

        # hm2_5i25.0.7i77.0.0.output-03
        # net SAIDA_FLEX <= motion.digital-out-12
        self.do_saida_flex = 12

        # hm2_5i25.0.7i77.0.0.output-00
        # net SAIDA_FLEX <= motion.digital-out-13
        self.do_triac_posicao_ok = 13

        self.triac_posicao = (-149, 0, 0)

    ######################################################
    # Segurança - Aguarda MDI OK

    def ok_for_mdi(self):
        s.poll()
        return not s.estop and s.enabled and s.homed \
               and (s.interp_state == linuxcnc.INTERP_IDLE)

    def aguarda_mdi_ok(self, nome_funcao):
        """Aguarda o ok_for_mdi; máquina ligada e emergência desabilitada."""
        while not self.ok_for_mdi():
            log.info(nome_funcao + ': aguardando MDI...')
            time.sleep(1)

    ######################################################
    # Propriedades

    @property
    def inicio_ciclo_abb(self):
        s.poll()
        return s.dout[self.do_inicio_ciclo_abb]

    @inicio_ciclo_abb.setter
    def inicio_ciclo_abb(self, val):
        assert val in (0, 1, True, False)
        log.info('Setando inicio_ciclo_abb para ' + str(val))
        c.mode(linuxcnc.MODE_MANUAL)
        c.set_digital_output(self.do_inicio_ciclo_abb, val)

    @property
    def triac_posicao_ok(self):
        s.poll()
        return s.dout[self.do_triac_posicao_ok]

    @triac_posicao_ok.setter
    def triac_posicao_ok(self, val):
        assert val in (0, 1, True, False)
        log.info('Setando triac_posicao_ok para ' + str(val))
        c.mode(linuxcnc.MODE_MANUAL)
        c.set_digital_output(self.do_triac_posicao_ok, val)

    @property
    def digital_abb(self):
        s.poll()
        return s.din[self.di_abb_bit0] << 2 | s.din[self.di_abb_bit1] << 1 | s.din[self.di_abb_bit2]

    @property
    def verificacao_ok(self):
        s.poll()
        return s.dout[self.do_verificacao_ok]

    @verificacao_ok.setter
    def verificacao_ok(self, val):
        assert val in (0, 1, True, False)
        log.info('Setando verificacao_ok para ' + str(val))
        c.mode(linuxcnc.MODE_MANUAL)
        c.set_digital_output(self.do_verificacao_ok, val)

    @property
    def saida_flex(self):
        s.poll()
        return s.dout[self.do_saida_flex]

    @saida_flex.setter
    def saida_flex(self, val):
        assert val in (0, 1, True, False)
        log.info('Setando saida_flex para ' + str(val))
        c.mode(linuxcnc.MODE_MANUAL)
        c.set_digital_output(self.do_saida_flex, val)

    @property
    def home_ok(self):
        s.poll()
        return all(s.homed[:3])

    ######################################################
    # Operações individuais

    def triac_ir_home(self):
        """
        Comanda o home dos 3 eixos do TRIAC, e em seguida aguarda 
        a compleção do processo. Não faz sentido aguardar mdi_ok aqui
        porque o mdi_ok depende da condição s.homed.
        """

        log.info('Fazendo home de todos os eixos.')
        self.triac_posicao_ok = False
        c.mode(linuxcnc.MODE_MANUAL)
        for i in range(3):
            c.home(i)
        while not self.home_ok:
            time.sleep(0.1)
        return self.home_ok

    def abrir_morsa(self, aguardar_mdi_ok=True):
        if aguardar_mdi_ok:
            self.aguarda_mdi_ok('abrir_morsa')
        c.mode(linuxcnc.MODE_MANUAL)
        c.set_digital_output(self.do_morsa_abre, 1)
        time.sleep(3)
        c.set_digital_output(self.do_morsa_abre, 0)

    def fechar_morsa(self, aguardar_mdi_ok=True):
        if aguardar_mdi_ok:
            self.aguarda_mdi_ok('fechar_morsa')
        log.info('Fechando morsa')
        c.mode(linuxcnc.MODE_MANUAL)
        c.set_digital_output(self.do_morsa_fecha, 1)
        time.sleep(4)
        c.set_digital_output(self.do_morsa_fecha, 0)

    def executar_programa(self):
        c.mode(linuxcnc.MODE_AUTO)
        # c.program_open("PROGRAMA_CNC.ngc")
        c.program_open(os.path.join(os.getcwd(), 'PROGRAMA_CNC.ngc'))
        c.auto(linuxcnc.AUTO_RUN, 0)
        self.aguarda_mdi_ok('executar_programa')
        c.mode(linuxcnc.MODE_MDI)

    def triac_ir_posicao(self):
        x, y, z = self.triac_posicao
        self.aguarda_mdi_ok('triac_ir_posicao (1)')
        c.mode(linuxcnc.MODE_MDI)
        c.mdi('G00 X' + str(x) + ' Y' + str(y) + ' Z' + str(z))
        self.aguarda_mdi_ok('triac_ir_posicao (2)')
        self.triac_posicao_ok = True

    # Comando do operador
    def celula_iniciar_ciclo_individual(self):
        """Pulsar início do ciclo abb"""
        self.inicio_ciclo_abb = True
        time.sleep(0.1)
        self.inicio_ciclo_abb = False

    # Comando do operador
    def celula_iniciar_ciclo_continuo(self):
        """Setar início do ciclo ABB"""
        self.inicio_ciclo_abb = True

    # Comando do operador
    def celula_parar_ciclo_continuo(self):
        """Resetar início do ciclo ABB"""
        self.inicio_ciclo_abb = False

    def pulsar_verificacao_ok(self):
        log.info('Pulsando verificação ok')
        self.verificacao_ok = 1
        time.sleep(1)
        self.verificacao_ok = 0

    # Rodado continuamente pra determinar ação em caso de comando da ABB
    def verificar_comando_abb(self):
        # Aguardamos 100ms caso as entradas não sejam 00, pra ter certeza de que as entradas tiveram tempo de
        # ser setadas corretamente
        if self.digital_abb != 0b000:
            time.sleep(0.1)

        if self.digital_abb == 0b001:
            log.info('Comando ABB - verificar_peca_boa')
            self.verificar_peca_boa()
        elif self.digital_abb == 0b010:
            log.info('Comando ABB - triac_iniciar_operacao')
            self.triac_iniciar_operacao()
        elif self.digital_abb == 0b011:
            log.info('Comando ABB - verificar_tem_peca_triac')
            self.verificar_tem_peca_triac()
        elif self.digital_abb == 0b100:
            log.info('Comando ABB - abrir_morsa')
            self.abrir_morsa()
            self.pulsar_verificacao_ok()
        elif self.digital_abb == 0b101:
            log.info('Comando ABB - fechar_morsa')
            self.fechar_morsa()
            self.pulsar_verificacao_ok()

    # Comando do ABB
    def triac_iniciar_operacao(self):
        self.triac_posicao_ok = False
        self.executar_programa()
        self.triac_ir_posicao()
        self.pulsar_verificacao_ok()
        # todo - verificar fluxograma (triac posição OK?)

    # Comando do ABB
    def verificar_tem_peca_triac(self):
        # todo - alg. visão
        tem_peca = raw_input('Tem peça triac? (s/n)')
        tem_peca = tem_peca.strip().lower() in ['s', 'y', '1']
        if tem_peca:
            self.saida_flex = 1
        else:
            self.saida_flex = 0
        self.pulsar_verificacao_ok()

    # Comando do ABB
    def verificar_peca_boa(self):
        # todo - alg. visão
        # peca_boa = raw_input('Peça boa? (s/n)')
        # peca_boa = peca_boa.strip().lower() in ['s', 'y', '1']
        # log.info('verificar_peca_boa')
        peca_boa = True
        time.sleep(1)
        if peca_boa:
            log.info('verificar_peca_boa_true')
            self.saida_flex = 1
        else:
            log.info('verificar_peca_boa_false')
            self.saida_flex = 0
        self.pulsar_verificacao_ok()

    def print_info(self):
        print('DO - inicio_ciclo_abb: %s' % self.inicio_ciclo_abb)
        print('DO - saida_flex: %s' % self.saida_flex)
        print('DO - verificacao_ok: %s' % self.verificacao_ok)
        print('DO - triac_posicao_ok: %s' % self.triac_posicao_ok)
        print('DI - digital_abb: %s' % self.digital_abb)


def debug_abb(lpi):
    while True:
        print("""
        ====================================================
        INPUT MANUAL DE TESTES
        Comandos:
        1  - (operador) Início Ciclo ABB
        2  - (operador) Início Ciclo ABB Contínuo
        3  - (operador) Fim Ciclo ABB Contínuo
        4  - (ciclo) TRIAC Ir Home
        5  - (ciclo) TRIAC Ir Posição
        6  - (ciclo) TRIAC Iniciar Operação
        7  - (ABB) Comanda Verificação de Peça TRIAC
        8  - (ABB) Comanda Verificação de Peça Boa
        9  - (ABB) Comanda Abre Morsa
        10 - (ABB) Comanda Fecha Morsa
        11 - Print Info
        """)

        cmd = raw_input('Comando: ').strip()

        if cmd == '1':
            lpi.celula_iniciar_ciclo_individual()
        elif cmd == '2':
            lpi.celula_iniciar_ciclo_continuo()
        elif cmd == '3':
            lpi.celula_parar_ciclo_continuo()
        elif cmd == '4':
            lpi.triac_ir_home()
        elif cmd == '5':
            lpi.triac_ir_posicao()
        elif cmd == '6':
            lpi.triac_iniciar_operacao()
        elif cmd == '7':
            lpi.verificar_tem_peca_triac()
        elif cmd == '8':
            lpi.verificar_peca_boa()
        elif cmd == '9':
            lpi.abrir_morsa()
        elif cmd == '10':
            lpi.fechar_morsa()
        elif cmd == '11':
            lpi.print_info()
        else:
            print('Comando inválido')


def rodar_logica_pi(conn):
    lpi = LogicaPI()

    # inicio
    lpi.inicio_ciclo_abb = 0
    lpi.verificacao_ok = 0
    lpi.triac_posicao_ok = 0

    lpi.triac_ir_home()
    lpi.triac_ir_posicao()

    # loop
    while True:
        if conn is not None and conn.poll():  # não blocante
            log.info('Recebido mensagem:')
            server_msg = conn.recv()
            print(server_msg)
            if server_msg['comando'] == 'iniciar_ciclo_individual':
                lpi.celula_iniciar_ciclo_individual()
            elif server_msg['comando'] == 'iniciar_ciclo_continuo':
                lpi.celula_iniciar_ciclo_continuo()
            elif server_msg['comando'] == 'parar_ciclo_continuo':
                lpi.celula_parar_ciclo_continuo()
            elif server_msg['comando'] == 'abrir_morsa':
                lpi.abrir_morsa()
            elif server_msg['comando'] == 'fechar_morsa':
                lpi.fechar_morsa()
            elif server_msg['comando'] == 'info':
                s.poll()
                axes = s.axis[:3]
                axes_positions = [round(axis['output'], 4) for axis in axes]
                x, y, z = axes_positions
                conn.send({
                    'inicio_ciclo_abb': lpi.inicio_ciclo_abb,
                    'verificacao_ok': lpi.verificacao_ok,
                    'saida_flex': lpi.saida_flex,
                    'triac_posicao_ok': lpi.triac_posicao_ok,
                    'digital_abb': lpi.digital_abb,
                    'home_ok': lpi.home_ok,
                    'triac_x': x,
                    'triac_y': y,
                    'triac_z': z
                })

        lpi.verificar_comando_abb()
        time.sleep(0.1)


if __name__ == '__main__':
    # /inicio

    debug = True
    if debug:
        lpi = LogicaPI()
        debug_abb(lpi)
    else:
        rodar_logica_pi(None)
