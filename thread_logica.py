# coding=utf-8
import logging
import time

try:
    import linuxcnc
except ImportError:
    log.info('Usando mock linuxcnc (sem efeitos reais)')
    import mock_linuxcnc as linuxcnc

log = logging.getLogger('logica')
s = linuxcnc.stat()
c = linuxcnc.command()

class LogicaPI(object):

    def __init__(self):

        self.di_abb_msb = None
        self.di_abb_lsb = None

        # hm2_5i25.0.7i77.0.0.output-07
        # net ABRE_MORSA <= motion.digital-out-05
        self.do_morsa_abre = 5

        # hm2_5i25.0.7i77.0.0.output-06
        # net FECHA_MORSA <= motion.digital-out-06
        self.do_morsa_fecha = 6

        # hm2_5i25.0.7i77.0.0.output-05
        # net INICIO_CICLO_ABB <= motion.digital-out-10
        self.do_inicio_ciclo_abb = 10

        # hm2_5i25.0.7i77.0.0.output-03
        # net SAIDA_FLEX <= motion.digital-out-12
        self.do_saida_flex = 12
        
        # hm2_5i25.0.7i77.0.0.output-02
        # net VERIFICACAO_OK <= motion.digital-out-11
        self.do_verificacao_ok = 11



        self.inicio_ciclo_abb = False
        self.triac_posicao_ok = False

        # self.saida_flex = 0
        # self.verificacao_ok = False

        # self.digital_abb = 0b00

        # todo - atualizar DO

        # self.triac_ir_home()
        # self.triac_ir_posicao()

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
    def digital_abb(self):
        s.poll()
        return self.di_abb_msb << 1 | self.di_abb_lsb

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
    # Segurança - Aguarda MDI OK

    def triac_ir_home(self):
        """
        Comanda o home dos 3 eixos do TRIAC, e em seguida aguarda 
        a compleção do processo. Não faz sentido aguardar mdi_ok aqui
        porque o mdi_ok depende da condição s.homed.
        """

        log.info('Fazendo home de todos os eixos.')
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
        time.sleep(2)
        c.set_digital_output(self.do_morsa_abre, 0)

    
    def fechar_morsa(self, aguardar_mdi_ok=True):
        if aguardar_mdi_ok:
            self.aguarda_mdi_ok('fechar_morsa')
        log.info('Fechando morsa')
        c.mode(linuxcnc.MODE_MANUAL)
        c.set_digital_output(self.do_morsa_fecha, 1)
        time.sleep(2)
        c.set_digital_output(self.do_morsa_fecha, 0)

        

    def executar_programa(self, nome_arquivo):
        c.program_open("foo.ngc")
        # todo


    def triac_ir_posicao(self):
        # Todo - mdi
        pass

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

    # Rodado continuamente pra determinar ação em caso de comando da ABB
    def verificar_comando_abb(self):
        # Aguardamos 100ms caso as entradas não sejam 00, pra ter certeza de que as entradas tiveram tempo de
        # ser setadas corretamente
        if self.digital_abb != 0b00:
            time.sleep(0.1)

        if self.digital_abb == 0b01:
            self.verificar_peca_boa()
        elif self.digital_abb == 0b10:
            self.triac_iniciar_operacao()
        elif self.digital_abb == 0b11:
            self.verificar_tem_peca_triac()

    # Comando do ABB
    def triac_iniciar_operacao(self):
        self.triac_posicao_ok = False
        # todo - atualizar DO
        # todo - MDI triac operação
        # todo - verificar fluxograma (triac posição OK?)

    # Comando do ABB
    def verificar_tem_peca_triac(self):
        # todo - alg. visão
        tem_peca = input('Tem peça triac? (s/n)')
        tem_peca = tem_peca.strip().lower() in ['s', 'y', '1']
        if tem_peca:
            self.saida_flex = 1
            self.verificacao_ok = True
        else:
            self.saida_flex = 0
            self.verificacao_ok = True
        time.sleep(0.1)
        self.verificacao_ok = False

    # Comando do ABB
    def verificar_peca_boa(self):
        # todo - alg. visão
        peca_boa = input('Peça boa? (s/n)')
        peca_boa = peca_boa.strip().lower() in ['s', 'y', '1']
        if peca_boa:
            self.saida_flex = 1
            self.verificacao_ok = True
        else:
            self.saida_flex = 0
            self.verificacao_ok = True
        time.sleep(0.1)
        self.verificacao_ok = False


if __name__ == '__main__':
    lpi = LogicaPI()
    lpi.triac_ir_home()
    print(lpi.home_ok)